import requests

# Create a single session object to be used by all API calls
api_session = requests.Session()

# Set the base headers for the session
dropdown_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://indiawris.gov.in',
    'Referer': 'https://indiawris.gov.in/dataSet/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
}
api_session.headers.update(dropdown_headers)

def initialize_session():
    """Establishes a session for the dropdown API calls by visiting the site."""
    try:
        setup_url = "https://indiawris.gov.in/dataSet/"
        response = api_session.get(setup_url, timeout=15)
        response.raise_for_status()
        print("✅ Session for dropdowns is fresh.")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ WARNING: Could not initialize session. Error: {e}")