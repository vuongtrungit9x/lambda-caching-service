import requests

def fetch_ga4_data(property_id, access_token, query):
    GA4_API_URL = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(GA4_API_URL, headers=headers, json=query)
    response.raise_for_status()

    return response.json()