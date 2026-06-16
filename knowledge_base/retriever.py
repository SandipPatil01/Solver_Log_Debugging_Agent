import json

def load_kb(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def simple_search(query, kb_data, top_k=5):
    query = query.lower()
    results = []

    for item in kb_data:
        text = item["text"].lower()

        score = sum(1 for word in query.split() if word in text)

        if score > 0:
            results.append((score, item))

    results.sort(reverse=True, key=lambda x: x[0])

    return [r[1] for r in results[:top_k]]