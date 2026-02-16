def detect_patterns(transactions):
    # minimal stub: returns matched patterns and aggregated metrics
    return {
        "incoming_count": len(transactions),
        "total_incoming": sum(tx.get("amount", 0) for tx in transactions),
        "patterns": ["structuring"] if len(transactions) > 10 else [],
    }
