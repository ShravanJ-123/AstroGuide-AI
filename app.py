from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from astrapy import DataAPIClient

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# API URLs and Key
API_URL_PLANET = "https://api.vedicastroapi.com/v3-json/horoscope/planet-report"
API_URL_GEM = "https://api.vedicastroapi.com/v3-json/extended-horoscope/gem-suggestion"
API_KEY = "fbf2e9d4-47fe-5bb9-a4ec-1a243ca55f44"

# Astra DB Connection
client = DataAPIClient("AstraCS:YHjGXrTelvIdwyLKdfQEikUg:0e3f97d040e889f40f693524220ddae0ed379dda640efc82ebe024627dc92585")
database = client.get_database("https://abaaa4b6-d3ac-4b2e-b373-4384569942fa-us-east-2.apps.astra.datastax.com")
collection = database.get_collection("data2")  # Using single collection

# Langflow API Account Configuration
account_config = {
    "ranveer": {
        "BASE_API_URL": "https://api.langflow.astra.datastax.com",
        "LANGFLOW_ID": "50f59f86-16d5-46db-abe2-c0995d97f2b0",
        "FLOW_ID": "d8ebfc94-89df-4aff-b5e3-c47e42fe8eeb",
        "APPLICATION_TOKEN": "AstraCS:LFkXXAlxYxteywlZGjriswnT:e66f1c22e2c623019400a117f9609928ee41947b0bc5f84a65e30b4ce4580179",
    }
}

@app.route('/', methods=["GET", "POST"])
def home():
    """Render the chatbot interface."""
    if request.method == "POST":
        # Get form data
        name = request.form["name"]  # Adding name field
        dob = request.form["dob"]
        tob = request.form["tob"]
        lat = request.form["lat"]
        lon = request.form["lon"]
        tz = request.form["tz"]
        planet = request.form["planet"]

        # Make request for Planet Report
        params = {
            "api_key": API_KEY,
            "dob": dob,
            "tob": tob,
            "lat": lat,
            "lon": lon,
            "tz": tz,
            "planet": planet,
            "lang": "en"
        }

        planet_response = requests.get(API_URL_PLANET, params=params)
        planet_data = planet_response.json()

        # Extract data from Planet API
        planet_report = None
        if planet_response.status_code == 200 and planet_data['status'] == 200:
            planet_report = planet_data['response'][0]

        # Make request for Gem Suggestion
        gem_params = {
            "api_key": API_KEY,
            "dob": dob,
            "tob": tob,
            "lat": lat,
            "lon": lon,
            "tz": tz,
            "lang": "en"
        }

        gem_response = requests.get(API_URL_GEM, params=gem_params)
        gem_data = gem_response.json()

        gem_report = None
        if gem_response.status_code == 200 and gem_data['status'] == 200:
            gem_report = gem_data['response']

        # Insert the data into the single "astrology_data" collection
        if planet_report and gem_report:
            data_to_insert = {
                "name": name,  # Storing user name
                "dob": dob,
                "tob": tob,
                "lat": lat,
                "lon": lon,
                "tz": tz,
                "planet_report": planet_report,
                "gem_report": gem_report
            }
            collection.insert_one(data_to_insert)

        return render_template("index.html", planet_report=planet_report, gem_report=gem_report)
    
    return render_template("index.html", planet_report=None, gem_report=None)


@app.route('/api/message', methods=['POST'])
def get_message():
    """Handle chat messages from the frontend."""
    data = request.get_json()
    name = data.get('name')
    message = data.get('message')
    account = "ranveer"  # Using a single account for now

    if not name or not message:
        return jsonify({"error": "Name and message are required"}), 400

    response = run_flow(name, message, account)
    return jsonify(response)

def run_flow(name, message, account):
    """Send the formatted message to the Langflow API."""
    config = account_config[account]
    api_url = f"{config['BASE_API_URL']}/lf/{config['LANGFLOW_ID']}/api/v1/run/{config['FLOW_ID']}"

    formatted_prompt = (
        f"You are an Astrology expert of {name}. "
        f"Your job is to analyze data of name: {name} and provide answers to the asked question. "
        f"User will ask you a question: {message}"
    )

    payload = {
        "input_value": formatted_prompt,
        "output_type": "chat",
        "input_type": "chat",
    }
    headers = {
        "Authorization": f"Bearer {config['APPLICATION_TOKEN']}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Extract only the 'text' field from the response
        text = "No response found."
        if isinstance(data, dict):
            outputs = data.get("outputs", [])
            if outputs:
                message_data = outputs[0].get("outputs", [{}])[0].get("results", {}).get("message", {})
                text = message_data.get("text", "No text found in the message.")

        print("Extracted Text:", text)  # Print extracted text

    except requests.RequestException as e:
        text = f"Error: Unable to reach the server ({e})."
    except Exception as e:
        text = f"Error: {str(e)}"

    return {"response": text}

if __name__ == "__main__":
    app.run(debug=True)
