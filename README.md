# CGWB-gw_data_extractor
This simple UI is meant to extract groundwater data collected by CGWB from the IndiaWRIS site. It bypasses the issues with swagger UI and allows you to download data for a whole district or state or UT in one go. The data is clustered using station code and arranged in chronological order in a csv file. 

The following packages need to be installed to run this locally:
requests
pandas
Flask
Flask-Cors
numpy

You can install all of them at once with the following command in your terminal:
pip install requests pandas Flask Flask-Cors numpy
