def explain_decision(risk_summary, transactions):
    # stub explanation generator
    reasons = []
    if risk_summary.get("incoming_count", 0) > 20:
        reasons.append("High number of incoming transfers")
    if risk_summary.get("total_incoming", 0) > 100000:
        reasons.append("Large aggregate incoming amount")
    return {"reasons": reasons, "matched_rules": ["STRUCTURING"]}
