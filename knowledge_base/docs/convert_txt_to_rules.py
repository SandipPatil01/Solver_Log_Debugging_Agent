import re

def extract_rules(file_path):
    rules = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Split by FATAL sections
    sections = re.split(r"FATAL\s+\d+", content)

    for section in sections:
        if not section.strip():
            continue

        lines = section.strip().split("\n")

        issue = ""
        cause = ""
        fixes = []
        keywords = []

        for line in lines:
            line = line.strip()

            # Extract keywords
            keywords.extend(re.findall(r"[A-Z_ ]{5,}", line))

            # Extract cause
            if "cause" in line.lower():
                cause = line.split(":")[-1].strip()

            # Extract fixes
            if "-" in line or "solution" in line.lower():
                fixes.append(line.replace("-", "").strip())

        if keywords:
            rules.append({
                "keywords": list(set(keywords))[:5],
                "issue": keywords[0],
                "cause": cause or "Refer documentation",
                "fix": fixes or ["Check model setup"]
            })

    return rules


if __name__ == "__main__":
    rules = extract_rules("analysis.txt")

    import json
    print(json.dumps(rules, indent=2))