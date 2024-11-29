def authenticate_request(event, config):
    headers = event.get("headers", {})
    received_token = headers.get("authorization")
    expected_token = config.get("token")

    if not received_token:
        return False, "Unauthorized: Missing Authorization header"
    if not received_token.startswith("Bearer "):
        return False, "Unauthorized: Invalid token format"

    token_value = received_token.split("Bearer ")[1]
    if token_value != expected_token:
        return False, "Unauthorized: Token mismatch"

    return True, None