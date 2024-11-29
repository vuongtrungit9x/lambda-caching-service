import requests


def handle_pixel_request():
    # Mock data for testing
    mock_data = {
        "status": "success",
        "data": {
            "id": 123,
            "name": "Mock User",
            "email": "mockuser@example.com",
        },
    }

    # Simulate actual API call
    try:
        response = requests.get("https://jsonplaceholder.typicode.com/posts")
        response.raise_for_status()  # Ensure the request was successful
        return response.json()
    except requests.RequestException:
        # Return mock data if the actual request fails
        return mock_data
