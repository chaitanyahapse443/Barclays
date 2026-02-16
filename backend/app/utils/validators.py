def validate_case_payload(payload: dict) -> bool:
    required = ["customer_id", "customer_name", "alerts"]
    return all(k in payload for k in required)
