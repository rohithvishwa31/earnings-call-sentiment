import numpy as np

def aggregate_results(results):

    scores = np.array([r["score"] for r in results])

    strong_signals = [r for r in results if abs(r["score"]) > 0.6]

    if len(strong_signals) >= 2:
        best = max(strong_signals, key=lambda x: abs(x["score"]))
        final_score = 0.7 * best["score"] + 0.3 * np.mean(scores)
    else:
        weights = np.exp(scores) / (np.sum(np.exp(scores)) + 1e-6)
        final_score = float(np.sum(weights * scores))

    final_score = max(min(final_score, 1.0), -1.0)

    drivers = []
    risks = []

    for r in results:
        drivers.extend(r["signals"]["positive"])
        risks.extend(r["signals"]["negative"])

    if final_score > 0.3:
        label = "positive"
    elif final_score < -0.3:
            label = "negative"
    else:
        label = "neutral"
    
    if len(drivers) >= 2 and final_score > 0:
        label = "positive"

    return {
        "label": label,
        "score": round(final_score, 4),
        "drivers": drivers[:3],
        "risks": risks[:3]
    }