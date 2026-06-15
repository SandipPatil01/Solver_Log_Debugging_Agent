def analyse_trends(parsed_data):
    observations = []

    # ✅ Safe access using .get()
    fatals = parsed_data.get("fatals", [])
    iterations = parsed_data.get("iterations", [])
    residuals = parsed_data.get("residuals", [])

    # ✅ Rule 1: Fatal present
    if len(fatals) > 0:
        observations.append("Run terminated due to fatal error")

    # ✅ Rule 2: Iteration issue
    if len(iterations) > 50:
        observations.append("High iteration count - possible convergence issue")

    # ✅ Rule 3: Residual issue
    if len(residuals) == 0:
        observations.append("No residual reduction observed")

    return observations