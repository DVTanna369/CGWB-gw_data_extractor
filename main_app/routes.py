import time
import io
import json
import pandas as pd
import numpy as np
from flask import Blueprint, request, jsonify
from urllib.parse import quote
from .api_client import api_session, initialize_session
from .helpers import download_paginated_data_post, convert_to_iso

bp = Blueprint('main', __name__)

@bp.route('/get-datasets', methods=['POST'])
def get_datasets():
    try:
        initialize_session()
        api_url = "https://indiawris.gov.in/DataSet/DataSetList"
        payload = {"headers": {"normalizedNames": {}, "lazyUpdate": None}}
        response = api_session.post(api_url, headers={'Content-Type': 'application/json'}, json=payload, timeout=15)
        response.raise_for_status()
        return jsonify(response.json().get('data', []))
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@bp.route('/get-states', methods=['POST'])
def get_states():
    try:
        initialize_session()
        request_data = request.get_json()
        dataset_code = request_data.get('datasetCode')
        if not dataset_code: return jsonify({"message": "datasetCode is required"}), 400
        api_url = "https://indiawris.gov.in/masterState/StateList"
        payload = {"datasetcode": dataset_code}
        response = api_session.post(api_url, headers={'Content-Type': 'application/json'}, json=payload, timeout=15)
        response.raise_for_status()
        return jsonify(response.json().get('data', []))
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@bp.route('/get-districts', methods=['POST'])
def get_districts():
    try:
        initialize_session()
        request_data = request.get_json()
        state_code = request_data.get('stateCode')
        dataset_code = request_data.get('datasetCode')
        if not state_code or not dataset_code: return jsonify({"message": "stateCode and datasetCode are required"}), 400
        api_url = "https://indiawris.gov.in/masterDistrict/getDistrictbyState"
        payload = {"statecode": state_code, "datasetcode": dataset_code}
        response = api_session.post(api_url, headers={'Content-Type': 'application/json'}, json=payload, timeout=15)
        response.raise_for_status()
        return jsonify(response.json().get('data', []))
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@bp.route('/get-rivers', methods=['POST'])
def get_rivers():
    try:
        initialize_session()
        request_data = request.get_json()
        dataset_code = request_data.get('datasetCode')
        if not dataset_code: return jsonify({"message": "datasetCode is required"}), 400
        api_url = "https://indiawris.gov.in/basin/getMasterBasin"
        payload = {"datasetcode": dataset_code}
        response = api_session.post(api_url, headers={'Content-Type': 'application/json'}, json=payload, timeout=15)
        response.raise_for_status()
        return jsonify(response.json().get('data', []))
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@bp.route('/get-tributaries', methods=['POST'])
def get_tributaries():
    try:
        initialize_session()
        request_data = request.get_json()
        basin_code = request_data.get('basinCode')
        dataset_code = request_data.get('datasetCode')
        if not basin_code or not dataset_code: return jsonify({"message": "basinCode and datasetCode are required"}), 400
        api_url = "https://indiawris.gov.in/masterTributary/getMasterTributary"
        payload = {"basincode": basin_code, "datasetcode": dataset_code}
        response = api_session.post(api_url, headers={'Content-Type': 'application/json'}, json=payload, timeout=15)
        response.raise_for_status()
        return jsonify(response.json().get('data', []))
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@bp.route('/get-agencies', methods=['POST'])
def get_agencies():
    try:
        initialize_session()
        request_data = request.get_json()
        payload = {
            "district_id": request_data.get("district_id", 0),
            "datasetcode": request_data.get("datasetcode", ""),
            "localriverid": 0,
            "tributaryid": request_data.get("tributaryid", 0)
        }
        api_url = "https://indiawris.gov.in/masterAgency/AgencyListInAnyCase"
        response = api_session.post(api_url, headers={'Content-Type': 'application/json'}, json=payload, timeout=15)
        response.raise_for_status()
        return jsonify(response.json().get('data', []))
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@bp.route('/download-data', methods=['POST'])
def download_data_endpoint():
    try:
        params = request.form.to_dict()
        data_category = params.get('dataCategory')
        dataset_name = params.get('datasetName')
        agency_name = params.get('agencyName')
        
        if not all([data_category, dataset_name, agency_name]):
            return jsonify({"message": "Dataset, Category, and Agency are required"}), 400

        # Parameters for the URL query string
        url_params = {'agencyName': agency_name}
        # Parameters for the POST body
        body_params = {
            'startdate': params.get('startdate', ''), 'enddate': params.get('enddate', ''),
            'size': 1000, 'download': 'true'
        }
        
        sort_keys = []
        filename = "download.csv"
        safe_dataset_name = dataset_name.replace(" ", "_").replace("/", "_")
        
        if data_category == 'admin':
            dataset_url_part = quote(dataset_name)
            base_url = f"https://indiawris.gov.in/Dataset/{dataset_url_part}"
            url_params['stateName'] = params.get('stateName')
            child_names_str = params.get('districtName', '')
            child_param_name = 'districtName'
            sort_keys = ['district', 'stationCode']
            district_name = "All_Districts" if ',' in child_names_str else child_names_str.replace(" ", "_")
            filename = f"{safe_dataset_name}_admin_data_{district_name}.csv"
        elif data_category == 'basin':
            dataset_url_part = "River%20WaterLevel" if dataset_name == "River Water Level" else quote(dataset_name)
            base_url = f"https://indiawris.gov.in/Dataset/Basin/{dataset_url_part}"
            url_params['basinName'] = params.get('riverName')
            child_names_str = params.get('tributaryName', '')
            child_param_name = 'tributaryName'
            sort_keys = ['tributary', 'stationCode']
            tributary_name = "All_Tributaries" if ',' in child_names_str else child_names_str.replace(" ", "_")
            filename = f"{safe_dataset_name}_basin_data_{tributary_name}.csv"
        else:
            return jsonify({"message": "Invalid data category"}), 400

        is_all_children = ',' in child_names_str
        child_list = child_names_str.split(',') if is_all_children else [child_names_str]
        
        all_child_dfs = []
        for child_name in child_list:
            if not child_name: continue
            
            current_url_params = url_params.copy()
            current_url_params[child_param_name] = child_name
            
            df = download_paginated_data_post(base_url, current_url_params, body_params)
            
            if df is not None and not df.empty:
                all_child_dfs.append(df)
            if is_all_children: time.sleep(0.5)

        if not all_child_dfs:
            return jsonify({"preview": [], "csvData": "", "totalRecords": 0, "filename": "no_data.csv"})

        final_df = pd.concat(all_child_dfs, ignore_index=True)
        
        df_sorted = final_df
        valid_sort_keys = [key for key in sort_keys if key in final_df.columns]
        if valid_sort_keys:
            df_sorted = final_df.sort_values(by=valid_sort_keys, na_position='last')
        
        if 'dataTime' in df_sorted.columns:
            df_sorted['dataTime'] = pd.to_datetime(df_sorted['dataTime'].apply(convert_to_iso), errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
        
        df_for_json = df_sorted.replace({np.nan: None})
        preview_data = df_for_json.head(100).to_dict(orient='records')
        output = io.StringIO()
        df_sorted.to_csv(output, index=False)
        csv_output = output.getvalue()
        
        return jsonify({
            "preview": preview_data,
            "csvData": csv_output,
            "totalRecords": len(df_sorted),
            "filename": filename
        })
    except Exception as e:
        return jsonify({"message": f"An internal server error occurred: {e}"}), 500