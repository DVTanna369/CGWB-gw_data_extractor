from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from urllib.parse import urljoin
import io
import numpy as np

# This imports the functions from your 'your_data_downloader.py' file
from your_data_downloader import download_paginated_data_post, convert_to_iso

app = Flask(__name__)
CORS(app)

@app.route('/download-data', methods=['POST'])
def download_data_endpoint():
    try:
        params = request.form.to_dict()
        
        district_names_str = params.get('districtName', '')
        # Check if the special value for all districts was sent, or if there's a comma
        is_all_districts = '__ALL__' in district_names_str or ',' in district_names_str
        
        if is_all_districts:
            # The frontend sends a comma-separated string of all districts
            district_list = district_names_str.split(',')
        else:
            district_list = [district_names_str]

        # Validation
        required_fields = ['stateName', 'startdate', 'enddate']
        missing_fields = [field for field in required_fields if not params.get(field)]
        if not district_list or not district_list[0]:
             missing_fields.append('districtName')

        if missing_fields:
            message = f"Missing required form fields: {', '.join(missing_fields)}"
            return jsonify({"message": message}), 400

        # Base parameters for the API calls
        base_params = {
            'agencyName': 'cgwb',
            'stateName': params['stateName'],
            'startdate': params['startdate'],
            'enddate': params['enddate'],
            'size': 1000,
            'download': 'true'
        }
        dataset = 'Ground%20Water%20Level'
        base_site = "https://indiawris.gov.in/Dataset/"
        base_url = urljoin(base_site, dataset)

        all_district_dfs = []
        
        # Loop through each district in the list
        for district in district_list:
            if not district: continue # Skip if a district name is empty for any reason

            print(f"\n--- Fetching data for District: {district} ---")
            current_params = base_params.copy()
            current_params['districtName'] = district
            
            # Handle the special API rule for multi-word districts
            state_name = current_params['stateName']
            if district.lower().endswith(state_name.lower()):
                cleaned_district = district.lower().replace(state_name.lower(), '').strip()
                current_params['districtName'] = cleaned_district.title()
            
            print(f"Request parameters sent to downloader: {current_params}")
            
            df = download_paginated_data_post(base_url, current_params)
            
            if df is not None:
                print(f"Successfully downloaded {len(df)} records for {district}.")
                all_district_dfs.append(df)
            else:
                print(f"No data found for {district}. Skipping.")

        if not all_district_dfs:
            return jsonify({"message": "No data could be downloaded for the selected criteria."}), 404

        # Combine all collected DataFrames into one
        final_df = pd.concat(all_district_dfs, ignore_index=True)

        if 'dataTime' in final_df.columns:
            final_df['dataTime'] = final_df['dataTime'].apply(convert_to_iso)
            final_df['dataTime'] = pd.to_datetime(final_df['dataTime']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            if is_all_districts:
                # Sort by District, then Station, then Time for the "All Districts" case
                sort_columns = [col for col in ['district', 'stationName', 'dataTime'] if col in final_df.columns]
            else:
                # Original sorting for the single district case
                sort_columns = [col for col in ['stationCode', 'dataTime'] if col in final_df.columns]
            
            if sort_columns:
                print(f"Sorting data by: {sort_columns}")
                df_sorted = final_df.sort_values(by=sort_columns)
            else:
                df_sorted = final_df
        else:
            df_sorted = final_df

        # Replace NaN with None for valid JSON
        df_for_json = df_sorted.replace({np.nan: None})

        # Prepare the 100-line preview
        preview_df = df_for_json.head(100).copy()

        # --- NEW: Reorder columns for the preview if "All Districts" is selected ---
        if is_all_districts and 'district' in preview_df.columns:
            cols = preview_df.columns.tolist()
            # Move the 'district' column to the front of the list
            cols.insert(0, cols.pop(cols.index('district')))
            # Reorder the preview DataFrame
            preview_df = preview_df[cols]
        
        preview_data = preview_df.to_dict(orient='records')


        # Prepare the full data as a CSV string (using the original sorted DataFrame)
        output = io.StringIO()
        df_sorted.to_csv(output, index=False)
        csv_output = output.getvalue()
        
        response_data = {
            "preview": preview_data,
            "csvData": csv_output,
            "totalRecords": len(df_sorted)
        }
        
        return jsonify(response_data)

    except Exception as e:
        print(f"An unhandled error occurred in the backend: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500

if __name__ == '__main__':
    app.run(debug=True)
