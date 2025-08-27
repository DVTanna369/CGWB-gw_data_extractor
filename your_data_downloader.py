import requests
import pandas as pd
import json
import ast

def download_paginated_data_post(base_url, initial_params):
    """
    Downloads data from a paginated API endpoint using a POST request.
    This version is robust and can extract the data list even if it is
    nested inside a dictionary in the API response.
    """
    all_data = []
    current_page = 0
    params = initial_params.copy()

    print("Starting data download using POST request...")

    while True:
        try:
            params['page'] = current_page
            print(f"Fetching data from page {current_page}...")
            
            response = requests.post(base_url, data=params, timeout=30)
            response.raise_for_status()
            
            response_json = response.json()
            data_list = None
            if isinstance(response_json, list):
                # Case 1: The server sent a plain list of records.
                data_list = response_json
            elif isinstance(response_json, dict):
                # Case 2: The server sent a dictionary. We need to find the list inside it.
                for value in response_json.values():
                    if isinstance(value, list):
                        data_list = value
                        break # Found the list, no need to look further
                
                if data_list is None:
                    # It was a dictionary, but contained no list. This might be an error message.
                    print(f"Server sent a dictionary with no data list: {response_json}. Stopping.")
                    break
            else:
                # The response is something else entirely (e.g., just a number or string)
                print(f"Server sent an unexpected data type: {type(response_json)}. Stopping.")
                break

            # Now, we check if the list we found is empty.
            if not data_list:
                print("Server response: Empty data list. Reached the last page.")
                break
            
            # If we get here, we have a valid list of data.
            all_data.extend(data_list)
            current_page += 1

        except json.JSONDecodeError:
            print("Could not parse JSON from server response. Assuming end of data.")
            print(f"Final server response text: {response.text}")
            break

        except requests.exceptions.HTTPError as e:
            print(f"An HTTP error occurred: {e}")
            print(f"Response body: {response.text}")
            break
        
        except requests.exceptions.RequestException as e:
            print(f"A network error occurred: {e}")
            return None

    if not all_data:
        print("Loop finished, but no data was collected.")
        return None

    print(f"Download complete. Total records found: {len(all_data)}")
    return pd.DataFrame(all_data)


def convert_to_iso(value):
    """
    Converts a dictionary or a string representation of a dictionary
    to an ISO 8601 datetime string.
    """
    try:
        # Check if the value is a string, and if so, safely evaluate it
        if isinstance(value, str):
            time_dict = ast.literal_eval(value)
        # If it's already a dictionary, use it directly
        else:
            time_dict = value
        
        # Now, with a dictionary, construct the ISO string
        iso_string = (
            f"{time_dict['year']:04d}-{time_dict['monthValue']:02d}-{time_dict['dayOfMonth']:02d} "
            f"{time_dict['hour']:02d}:{time_dict['minute']:02d}:{time_dict['second']:02d}"
        )
        return iso_string
    except (ValueError, SyntaxError, KeyError):

        return None
