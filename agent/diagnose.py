from Knowledge.rules import RULES

def diagnose(parsed_data, observations):
    diagnosis = []
    matched_issues = set()   # to avoid duplicate results

    fatals = parsed_data.get("fatals", [])

    # ✅ Loop through all fatal blocks
    for fatal in fatals:
        fatal_clean = fatal.lower()

        print("\n--- Checking Fatal Block ---")
        print(fatal)

        # ✅ Check each rule
        for rule in RULES:
            for keyword in rule["keywords"]:
                
                # ✅ Case-insensitive matching
                if keyword.lower() in fatal_clean:

                    # ✅ Avoid duplicate reporting
                    if rule["issue"] not in matched_issues:
                        print(f"✅ MATCH FOUND: {rule['issue']}")

                        diagnosis.append({
                            "issue": rule["issue"],
                            "cause": rule["cause"],
                            "fix": rule["fix"],
                            "matched_keyword": keyword,
                            "evidence": fatal.strip()
                        })

                        matched_issues.add(rule["issue"])

    # ✅ If nothing matched
    if not diagnosis:
        diagnosis.append({
            "issue": "Unknown Issue",
            "cause": "No rule matched with detected fatal messages",
            "fix": [
                "Check full solver log manually",
                "Expand knowledge base with this failure pattern",
                "Verify solver input deck and boundary conditions"
            ],
            "matched_keyword": None,
            "evidence": None
        })

    return diagnosis