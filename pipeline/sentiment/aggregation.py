def aggregate_results(results):
    total_score = 0
    total_weight = 0

    drivers = []
    risks = []

    for r in results:
        score = r["score"]
        weight = r.get("weight", 1.0)

        total_score += score * weight
        total_weight += weight

        drivers.extend(r["signals"]["positive"])
        risks.extend(r["signals"]["negative"])

    avg = total_score / (total_weight + 1e-6)

    if avg > 0.05:
        label = "positive"
    elif avg < -0.05:
            label = "negative"
    else:
        label = "neutral"
    
    if len(drivers) >= 2 and avg > 0:
        label = "positive"

    return {
        "label": label,
        "score": round(avg, 4),
        "drivers": drivers[:3],
        "risks": risks[:3]
    }