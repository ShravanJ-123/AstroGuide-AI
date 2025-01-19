from flask import Flask, render_template, request
import requests
from astrapy import DataAPIClient

app = Flask(__name__)

# API URLs and Key
API_URL_PLANET = "https://api.vedicastroapi.com/v3-json/horoscope/planet-report"
API_URL_GEM = "https://api.vedicastroapi.com/v3-json/extended-horoscope/gem-suggestion"
API_KEY = "fbf2e9d4-47fe-5bb9-a4ec-1a243ca55f44"

# Astra DB Connection
client = DataAPIClient("AstraCS:YHjGXrTelvIdwyLKdfQEikUg:0e3f97d040e889f40f693524220ddae0ed379dda640efc82ebe024627dc92585")
database = client.get_database("https://abaaa4b6-d3ac-4b2e-b373-4384569942fa-us-east-2.apps.astra.datastax.com")
collection = database.get_collection("data2")  # Using single collection

@app.route("/", methods=["GET", "POST"])
def index():
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

if __name__ == "__main__":
    app.run(debug=True)
