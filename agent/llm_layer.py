import os
import json
from difflib import SequenceMatcher

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# =========================================================
# KNOWLEDGE BASE LOADING
# =========================================================
KB_PATH = "knowledge_base/indexed_chunks.json"


def load_kb(file_path=KB_PATH):
    """
    Load local knowledge base chunks from JSON.
    Returns empty list if file does not exist or cannot be read.
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


KB_DATA = load_kb()


# =========================================================
# TEXT / NLP HELPERS
# =========================================================
def _normalise(text):
    return (text or "").strip().lower()


def simple_search(query, kb_data, top_k=5):
    """
    Very simple keyword-based retrieval from local knowledge chunks.
    Scores chunks by word overlap with the query.
    """
    query = _normalise(query)
    if not query or not kb_data:
        return []

    results = []

    for item in kb_data:
        text = _normalise(item.get("text", ""))

        score = sum(1 for word in query.split() if word in text)

        if score > 0:
            results.append((score, item))

    results.sort(reverse=True, key=lambda x: x[0])

    return [r[1] for r in results[:top_k]]


def infer_relevant_fix(user_question, fixes, selected_fix=None):
    """
    Decide which fix item the user is most likely asking about.
    Priority:
    1. Explicit fix selected in UI
    2. Similarity matching between question and fixes
    """
    if selected_fix and selected_fix != "General issue":
        return selected_fix

    if not fixes:
        return None

    q = _normalise(user_question)
    if not q:
        return None

    best_fix = None
    best_score = 0.0

    for fix in fixes:
        fix_norm = _normalise(fix)

        # word overlap
        overlap = 0
        for word in fix_norm.split():
            if word and word in q:
                overlap += 1

        # fuzzy similarity
        similarity = SequenceMatcher(None, q, fix_norm).ratio()

        score = overlap + similarity

        if score > best_score:
            best_score = score
            best_fix = fix

    # conservative threshold
    if best_score >= 0.6:
        return best_fix

    return None


def build_retrieval_query(issue, cause, user_question, chosen_fix=None):
    """
    Build a retrieval query for knowledge-base search.
    """
    parts = [issue or "", cause or "", user_question or ""]
    if chosen_fix:
        parts.append(chosen_fix)
    return " ".join(parts).strip()


def format_retrieved_context(chunks):
    """
    Format chunks for grounding the LLM response.
    """
    if not chunks:
        return "No relevant manual/documentation snippets were found."

    formatted = []
    for chunk in chunks:
        source = chunk.get("source", "unknown_source")
        page = chunk.get("page", None)
        text = chunk.get("text", "")

        if page:
            formatted.append(f"[Source: {source}, Page: {page}]\n{text}")
        else:
            formatted.append(f"[Source: {source}]\n{text}")

    return "\n\n".join(formatted)


# =========================================================
# DETERMINISTIC FALLBACK
# =========================================================
def answer_followup_fallback(issue, cause, fixes, user_question, selected_fix=None):
    """
    Deterministic fallback if LLM is unavailable.
    """
    chosen_fix = infer_relevant_fix(user_question, fixes, selected_fix)
    q = _normalise(user_question)

    if not issue:
        return "Please upload a solver log file first so I can analyse the issue."

    if chosen_fix:
        if "how" in q or "fix" in q or "apply" in q or "check" in q or "step" in q:
            return (
                f"**Focused fix item:** {chosen_fix}\n\n"
                f"**Issue:** {issue}\n\n"
                f"**Root cause:** {cause}\n\n"
                "**Suggested actions:**\n"
                f"- Start with: {chosen_fix}\n"
                "- Review the related model or run setup carefully\n"
                "- Re-run the job and check whether the fatal message is resolved"
            )

        return (
            f"**Focused fix item:** {chosen_fix}\n\n"
            f"This recommendation is related to the issue **{issue}**.\n\n"
            f"**Root cause:** {cause}"
        )

    if "cause" in q or "why" in q:
        return f"**Root cause:** {cause}"

    if "fix" in q or "how" in q:
        if fixes:
            return "**Recommended actions:**\n\n" + "\n".join([f"- {x}" for x in fixes])
        return "No fix recommendations are available yet."

    return (
        f"**Issue:** {issue}\n\n"
        f"**Root cause:** {cause}\n\n"
        + ("**Recommended fixes:**\n" + "\n".join([f"- {x}" for x in fixes]) if fixes else "")
    )


# =========================================================
# MAIN LLM RESPONSE FUNCTION
# =========================================================
def answer_followup_with_llm(issue, cause, fixes, user_question, selected_fix=None):
    """
    Main function used by app.py

    Uses:
    1. Rule-based diagnosis context
    2. Retrieved manual/documentation chunks from local knowledge base
    3. LLM-based answer generation
    4. Deterministic fallback if LLM fails
    """
    if not issue:
        return "Please upload a solver log file first so I can analyse the issue."

    chosen_fix = infer_relevant_fix(user_question, fixes, selected_fix)

    # Build retrieval query
    retrieval_query = build_retrieval_query(issue, cause, user_question, chosen_fix)

    # Retrieve relevant KB chunks
    retrieved_chunks = simple_search(retrieval_query, KB_DATA, top_k=5)
    retrieved_context = format_retrieved_context(retrieved_chunks)

    # If OpenAI SDK not installed, fallback
    if OpenAI is None:
        return answer_followup_fallback(issue, cause, fixes, user_question, selected_fix)

    # Read API key from environment (recommended)
    api_key = os.getenv("OPENAI_API_KEY")

    # If no API key, fallback
    if not api_key:
        return answer_followup_fallback(issue, cause, fixes, user_question, selected_fix)

    try:
        client = OpenAI(api_key=api_key)

        fixes_text = "\n".join([f"- {x}" for x in fixes]) if fixes else "No fix recommendations available."
        focus_text = chosen_fix if chosen_fix else "General issue context"

        system_prompt = """
You are a CAE solver debugging assistant for Nastran-style solver failures.

Your job:
- Answer follow-up questions about the diagnosed issue
- Use the provided issue, cause, fix list, and retrieved manual/documentation snippets
- If a specific fix item is in focus, centre the answer on that fix
- Be beginner-friendly, practical, and engineering-oriented
- Use plain English
- Prefer bullet points when giving steps
- Do not invent solver-specific facts not present in the supplied context
- If context is limited, say so clearly and give the safest practical guidance
"""

        user_prompt = f"""
Diagnosed issue:
{issue}

Root cause:
{cause}

Available fix recommendations:
{fixes_text}

Focused fix item:
{focus_text}

Relevant documentation / manual snippets:
{retrieved_context}

User question:
{user_question}

Please answer clearly and helpfully. If useful, include:
- what it means
- why it happens
- what to check
- step-by-step actions
- mention which source snippet supports the answer when possible
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        answer = response.choices[0].message.content.strip()

        # Optional: append source list to make answer more traceable
        if retrieved_chunks:
            sources = []
            seen = set()

            for chunk in retrieved_chunks:
                src = chunk.get("source", "unknown_source")
                page = chunk.get("page", None)

                label = f"{src} (Page {page})" if page else src
                if label not in seen:
                    seen.add(label)
                    sources.append(f"- {label}")

            answer += "\n\n**Reference snippets used:**\n" + "\n".join(sources)

        return answer

    except Exception:
        return answer_followup_fallback(issue, cause, fixes, user_question, selected_fix)
    
def answer_general_nastran_query(user_question):
    """
    Handles general Nastran-related questions using knowledge base only.
    """

    # ✅ If KB is empty → fallback
    if not KB_DATA:
        return "Knowledge base is not available yet. Please build it first."

    # ✅ Retrieve relevant chunks
    retrieved_chunks = simple_search(user_question, KB_DATA, top_k=5)
    retrieved_context = format_retrieved_context(retrieved_chunks)

    # ✅ Fallback if no LLM
    if OpenAI is None:
        return f"""
I found some relevant information:

{retrieved_context}

Please refer to the above content for guidance.
"""

    import os
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return f"""
I found some relevant information:

{retrieved_context}

(LLM not configured — showing raw knowledge base content)
"""

    try:
        client = OpenAI(api_key=api_key)

        system_prompt = """
You are a Nastran solver expert assistant.

You answer general questions about:
- Nastran cards
- solver behaviour
- error messages
- modelling best practices

Rules:
- Explain in simple engineering terms
- Be beginner-friendly
- Use the provided documentation snippets
- Do not invent facts outside provided context unless necessary
"""

        user_prompt = f"""
Relevant documentation:

{retrieved_context}

User question:
{user_question}

Provide a clear and practical explanation.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return f"""
LLM failed. Showing relevant documentation:

{retrieved_context}
"""