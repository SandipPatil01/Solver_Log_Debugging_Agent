import streamlit as st
import hashlib

from Parser.nastran_parser import parse_f06
from Observer.trend_analysis import analyse_trends
from agent.diagnose import diagnose
from agent.troubleshooting import get_troubleshooting_steps
from agent.llm_layer import answer_followup_with_llm, answer_general_nastran_query

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Solver Log Agent", layout="wide")

st.markdown(
    """
    <style>
    .sticky-panel {
        position: sticky;
        top: 1rem;
    }
    .small-muted {
        color: #6b7280;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SESSION STATE INITIALISATION
# =========================================================
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 0

if "followup_text" not in st.session_state:
    st.session_state.followup_text = ""

if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_file_signature" not in st.session_state:
    st.session_state.last_file_signature = None

if "current_issue" not in st.session_state:
    st.session_state.current_issue = None

if "current_cause" not in st.session_state:
    st.session_state.current_cause = None

if "current_fixes" not in st.session_state:
    st.session_state.current_fixes = []

if "current_steps" not in st.session_state:
    st.session_state.current_steps = []

if "selected_fix_context" not in st.session_state:
    st.session_state.selected_fix_context = "General issue"

# =========================================================
# HELPERS
# =========================================================
def reset_for_new_file():
    st.session_state.wizard_step = 0
    st.session_state.messages = []
    st.session_state.clear_input = True
    st.session_state.current_issue = None
    st.session_state.current_cause = None
    st.session_state.current_fixes = []
    st.session_state.current_steps = []
    st.session_state.selected_fix_context = "General issue"


# =========================================================
# LAYOUT
# =========================================================
main_col, side_col = st.columns([3, 1])

# Make these visible outside the layout blocks
uploaded_file = None
ask_clicked = False
clear_clicked = False

# =========================================================
# LEFT PANEL (MAIN AREA)
# =========================================================
with main_col:
    st.title("🔍 Solver Log Agent")
    st.info("Upload a solver log file (.f06 or .out) to diagnose solver issues, or use the assistant on the right for general Nastran questions.")

    uploaded_file = st.file_uploader("Upload solver log", type=["f06", "out"])

    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        file_signature = hashlib.md5(file_bytes).hexdigest()

        # Reset all diagnosis/chat state when a DIFFERENT file is uploaded
        if st.session_state.last_file_signature != file_signature:
            reset_for_new_file()
            st.session_state.last_file_signature = file_signature

        # Save uploaded file temporarily
        with open("temp.f06", "wb") as f:
            f.write(file_bytes)

        # Run pipeline
        parsed = parse_f06("temp.f06")
        observations = analyse_trends(parsed)
        diagnosis = diagnose(parsed, observations)

        if diagnosis:
            selected_diag = diagnosis[0]

            st.session_state.current_issue = selected_diag.get("issue", "Unknown Issue")
            st.session_state.current_cause = selected_diag.get("cause", "No cause identified")
            st.session_state.current_fixes = selected_diag.get("fix", [])
            st.session_state.current_steps = get_troubleshooting_steps(st.session_state.current_issue)

            issue = st.session_state.current_issue
            cause = st.session_state.current_cause
            fixes = st.session_state.current_fixes

            st.success("✅ Analysis Complete")
            st.divider()

            left_diag, right_diag = st.columns(2)

            with left_diag:
                st.markdown("## 🚨 Issue")
                st.error(issue)

                st.markdown("## 🔍 Root Cause")
                st.info(cause)

            with right_diag:
                st.markdown("## 🛠 Fix Recommendations")
                if fixes:
                    for i, fix in enumerate(fixes, start=1):
                        st.success(f"{i}. {fix}")
                else:
                    st.warning("No fix recommendation available yet.")

            st.divider()

            st.subheader("🧭 Guided Troubleshooting")
            steps = st.session_state.current_steps

            if steps:
                if st.session_state.wizard_step >= len(steps):
                    st.session_state.wizard_step = len(steps) - 1
                if st.session_state.wizard_step < 0:
                    st.session_state.wizard_step = 0

                current_step = steps[st.session_state.wizard_step]
                step_number = st.session_state.wizard_step + 1
                total_steps = len(steps)

                st.progress(step_number / total_steps)
                st.markdown(f"### Step {step_number} of {total_steps}: {current_step['title']}")
                st.write(current_step["instruction"])
                st.caption(f"Expected result: {current_step['expected']}")

                nav1, nav2, _ = st.columns([1, 1, 4])

                with nav1:
                    if st.button("⬅ Previous", disabled=st.session_state.wizard_step == 0):
                        st.session_state.wizard_step -= 1
                        st.rerun()

                with nav2:
                    if st.button("Next ➡", disabled=st.session_state.wizard_step == total_steps - 1):
                        st.session_state.wizard_step += 1
                        st.rerun()
            else:
                st.warning("No troubleshooting guide available for this issue yet.")

    else:
        # Clear diagnosis state when no file is uploaded
        st.session_state.current_issue = None
        st.session_state.current_cause = None
        st.session_state.current_fixes = []
        st.session_state.current_steps = []
        st.session_state.selected_fix_context = "General issue"

        st.markdown("### Welcome")
        st.write("You can use this tool in two ways:")
        st.markdown(
            """
            1. **Upload a solver log** to get a diagnosis, root cause, and fix recommendations  
            2. **Ask general Nastran questions** in the assistant panel on the right
            """
        )

# =========================================================
# RIGHT PANEL (ALWAYS VISIBLE)
# =========================================================
with side_col:
    st.markdown('<div class="sticky-panel">', unsafe_allow_html=True)

    st.markdown("## 💬 Assistant")

    if uploaded_file is None:
        st.markdown(
            '<div class="small-muted">General Nastran assistant mode — ask about cards, solver behaviour, fatal errors, or best practices.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="small-muted">Debugging assistant mode — ask about the diagnosed issue or a specific fix item.</div>',
            unsafe_allow_html=True
        )

    # Context selector
    current_fixes = st.session_state.current_fixes
    focus_options = ["General issue"] + current_fixes if current_fixes else ["General issue"]

    st.markdown("### Focus Area")
    selected_focus = st.selectbox(
        "Choose context",
        options=focus_options,
        key="selected_fix_context"
    )

    st.markdown("---")
    st.markdown("### Quick prompts")

    if uploaded_file is None:
        # General Nastran prompts
        if st.button("What is SPC?", use_container_width=True):
            st.session_state.followup_text = "What is SPC in Nastran?"

        if st.button("Explain GRID card", use_container_width=True):
            st.session_state.followup_text = "Explain GRID card in Nastran"

        if st.button("Common fatal errors", use_container_width=True):
            st.session_state.followup_text = "What are common fatal errors in Nastran?"

        if st.button("Constraint best practices", use_container_width=True):
            st.session_state.followup_text = "What are constraint best practices in Nastran?"
    else:
        # Diagnosis-specific prompts
        if st.button("Explain the selected fix", use_container_width=True):
            if selected_focus == "General issue":
                st.session_state.followup_text = "Explain this issue simply"
            else:
                st.session_state.followup_text = f"Explain how to apply this fix: {selected_focus}"

        if st.button("What should I check first?", use_container_width=True):
            if selected_focus == "General issue":
                st.session_state.followup_text = "What should I check first?"
            else:
                st.session_state.followup_text = f"What should I check first for this fix: {selected_focus}"

        if st.button("Give step-by-step guidance", use_container_width=True):
            if selected_focus == "General issue":
                st.session_state.followup_text = "Give me step-by-step guidance to fix this issue"
            else:
                st.session_state.followup_text = f"Give me step-by-step guidance for this fix: {selected_focus}"

        if st.button("How can I prevent this?", use_container_width=True):
            if selected_focus == "General issue":
                st.session_state.followup_text = "How can I prevent this next time?"
            else:
                st.session_state.followup_text = f"How can I prevent this issue related to this fix: {selected_focus}"

    st.markdown("---")
    st.markdown("### Ask your question")

    # Safe reset BEFORE widget creation
    if st.session_state.clear_input:
        st.session_state.followup_text = ""
        st.session_state.clear_input = False

    followup_prompt = st.text_area(
        "Your question",
        key="followup_text",
        height=120,
        placeholder="Example: What is SPC in Nastran? or How do I check boundary conditions?"
    )

    ask_clicked = st.button("Ask", use_container_width=True)
    clear_clicked = st.button("Clear question", use_container_width=True)

    if clear_clicked:
        st.session_state.clear_input = True
        st.rerun()

    st.markdown("---")
    st.markdown("### Conversation")

    if st.session_state.messages:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**🧑 You:** {msg['content']}")
            else:
                st.markdown(f"**🤖 Agent:** {msg['content']}")
    else:
        st.caption("No conversation yet.")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# FOLLOW-UP HANDLER
# =========================================================
if ask_clicked and st.session_state.followup_text.strip():
    user_question = st.session_state.followup_text.strip()

    st.session_state.messages.append({
        "role": "user",
        "content": user_question
    })

    # IMPORTANT CORRECTION:
    # Decide mode based on uploaded_file, NOT on old session issue values
    if uploaded_file is None:
        response = answer_general_nastran_query(user_question)
    else:
        response = answer_followup_with_llm(
            issue=st.session_state.current_issue,
            cause=st.session_state.current_cause,
            fixes=st.session_state.current_fixes,
            user_question=user_question,
            selected_fix=st.session_state.selected_fix_context
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    st.session_state.clear_input = True
    st.rerun()