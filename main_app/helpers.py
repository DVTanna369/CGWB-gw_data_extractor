import requests
import pandas as pd
import ast

def download_paginated_data_post(base_url, url_params, body_params):
    """
    Downloads data using a POST request where some parameters are in the URL
    and others are in the request body.
    """
    all_data = []
    current_page = 0
    
    post_headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://indiawris.gov.in',
        'Referer': 'https://indiawris.gov.in/dataSet/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
    }
    
    current_body_params = body_params.copy()

    while True:
        try:
            current_body_params['page'] = current_page
            print(f"Fetching data from page {current_page}...")
            
            # Use both `params` (for URL) and `data` (for body)
            response = requests.post(
                base_url, 
                params=url_params, 
                data=current_body_params, 
                headers=post_headers, 
                timeout=30
            )
            response.raise_for_status()
            
            response_json = response.json()
            data_list = response_json.get('data', []) if isinstance(response_json, dict) else response_json

            if not data_list or not isinstance(data_list, list):
                print("Reached the last page or received an empty/invalid data list.")
                break
            
            all_data.extend(data_list)
            current_page += 1

        except requests.exceptions.RequestException as e:
            print(f"A network error occurred during pagination: {e}")
            break
            
    if not all_data:
        return None

    print(f"Download complete. Total records found: {len(all_data)}")
    return pd.DataFrame(all_data)


def convert_to_iso(value):
    """Converts a dictionary string from the API into an ISO datetime string."""
    try:
        time_dict = ast.literal_eval(value) if isinstance(value, str) else value
        return (f"{time_dict['year']:04d}-{time_dict['monthValue']:02d}-{time_dict['dayOfMonth']:02d} "
                f"{time_dict['hour']:02d}:{time_dict['minute']:02d}:{time_dict['second']:02d}")
    except (ValueError, SyntaxError, KeyError, TypeError):
        return None