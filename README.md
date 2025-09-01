This project provides a user-friendly web interface for fetching, previewing, and downloading various datasets from the India Water Resources Information System (India-WRIS). It acts as a proxy, handling complex API interactions in the backend while offering a clean and dynamic form in the frontend.

Features
Dynamic Dependent Dropdowns: Sequentially load options for Data Category, State/River, District/Tributary, and Agency based on previous selections.

Dual Data Categories: Switch between an Admin view (State/District) and a Basin view (River/Tributary).

Intelligent Agency Filtering: Automatically filters the agency list to show only national bodies (CWC/CGWB) and handles cases where no data is available.

Custom Sorting & Filenames: Automatically sorts the downloaded data based on the selected category and generates descriptive, dynamic filenames.

Clean Architecture: The project is separated into a Python/Flask backend for API interaction and a vanilla JavaScript frontend for the user interface.

Project Structure
The project is organized into two main parts: a Python backend and a JavaScript frontend.

Backend Structure
/your_project_folder
├── app.py              # Main entry point to run the server
└── /main_app
    ├── __init__.py     # Creates the Flask app
    ├── api_client.py   # Manages the session and API communication
    ├── helpers.py      # Data processing and download functions
    └── routes.py       # All API endpoints (@app.route)

Frontend Structure
/your_project_folder
├── index.html          # The main HTML page
├── style.css           # All CSS styles
└── /js
    ├── main.js         # Main script with event listeners (Controller)
    ├── api.js          # All data fetching functions (Model)
    └── ui.js           # All functions that update the webpage (View)

Dependencies
The backend requires Python and the following packages:

Flask

Flask-Cors

requests

pandas

numpy

Installation
Navigate to the root directory of the backend project in your terminal.

Install all the required packages using the provided requirements.txt file:

pip install -r requirements.txt

How to Run on Localhost
To run this application, you need to have two terminals open simultaneously: one for the backend server and one for the frontend server.

Step 1: Start the Backend Server
Open a terminal or command prompt.

Navigate to the root directory of the backend (the folder containing app.py).

Run the Flask application:

python app.py

You should see output indicating the server is running on http://127.0.0.1:5000. Leave this terminal running.

Step 2: Start the Frontend Server
Open a new, separate terminal.

Navigate to the root directory of the frontend (the folder containing index.html).

Start Python's simple HTTP server:

# For Python 3
python -m http.server

# For Python 2
python -m SimpleHTTPServer

You should see a message like Serving HTTP on 0.0.0.0 port 8000. Leave this terminal running.

Step 3: Open the Webpage
Open your web browser (e.g., Chrome, Firefox).

Go to the following address:

http://localhost:8000

The webpage should now load and be fully functional.
