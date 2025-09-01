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

def pivot_data(df, data_category):
    """
    Transforms raw data into a wide-format pivoted table, ensuring all stations
    from the original file are preserved in the final output.
    """
    print(f"--- Pivoting data for '{data_category}' category ---")
    try:
        # Step 1: Standardize Column Names and Clean Station Codes
        df.columns = [col.lower() for col in df.columns]
        if 'stationcode' not in df.columns:
            print("Warning: 'stationcode' column not found.")
            return df
        
        df.dropna(subset=['stationcode'], inplace=True)
        df['stationcode'] = df['stationcode'].astype(str).str.strip()

        # Step 2: Create a Canonical Master List of ALL Stations
        print("\n--- Creating master list of all unique stations ---")
        
        # ✅ FIX: Define aggregation rules based on the selected data category
        possible_agg_rules = {
            'stationname': 'first',
            'unit': 'first',
            'latitude': 'mean',
            'longitude': 'mean',
            'welldepth': 'mean'
        }
        
        if data_category == 'admin':
            possible_agg_rules.update({'district': 'first', 'tehsil': 'first'})
        elif data_category == 'basin':
            possible_agg_rules.update({'basin': 'first', 'tributary': 'first'})

        # Filter rules to only include columns that actually exist in the dataframe
        agg_rules = {col: rule for col, rule in possible_agg_rules.items() if col in df.columns}
        
        station_info_df = df.groupby('stationcode').agg(agg_rules).reset_index()

        # Step 3: Prepare the Data for Pivoting
        df_for_pivot = df.copy()
        df_for_pivot.dropna(subset=['datavalue'], inplace=True)
        
        df_for_pivot['datatime'] = df_for_pivot['datatime'].apply(convert_to_iso)
        df_for_pivot['datatime'] = pd.to_datetime(df_for_pivot['datatime'])
        df_for_pivot['year'] = df_for_pivot['datatime'].dt.year

        # Step 4: Pivot ONLY the Data with Valid Values
        print("\n--- Pivoting yearly data values ---")
        pivoted_values_df = df_for_pivot.pivot_table(
            index='stationcode',
            columns='year',
            values='datavalue',
            aggfunc='mean'
        ).reset_index()
        pivoted_values_df.columns.name = None
        
        # Step 5: Merge the Master Station List with the Pivoted Data
        print("\n--- Merging station information with pivoted data ---")
        final_df = pd.merge(station_info_df, pivoted_values_df, on='stationcode', how='left')
        
        # Final cleanup for a clean CSV export
        obj_cols = final_df.select_dtypes(include=['object']).columns
        final_df[obj_cols] = final_df[obj_cols].fillna('')

        return final_df

    except Exception as e:
        print(f"An error occurred during pivoting: {e}")
        return df

