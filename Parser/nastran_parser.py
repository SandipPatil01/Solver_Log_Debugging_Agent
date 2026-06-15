def parse_f06(file_path):
    results = {
        "fatals": []
    }

    with open(file_path, "r", errors="ignore") as f:
        lines = f.readlines()

    current_block = []

    for line in lines:
        if "FATAL" in line.upper():
            if current_block:
                results["fatals"].append(" ".join(current_block))
                current_block = []

            current_block.append(line.strip())
        elif current_block:
            current_block.append(line.strip())

    if current_block:
        results["fatals"].append(" ".join(current_block))

    return results