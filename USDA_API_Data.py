import requests
import os

#reading API key - the key.txt file must be in the same folder

base_dir = os.path.dirname(os.path.abspath(__file__))

try:
    with open(os.path.join(base_dir,'key.txt'), 'r') as f:
        api_key = f.read().strip()
        print(f"Key: {api_key}")
except FileNotFoundError:
    raise FileNotFoundError("No API key found.")


Base_URL = "https://quickstats.nass.usda.gov/api/api_GET/"

#Dictionary containing sentiment score scale
Sentiment_Scores = {
    "PCT VERY POOR": -1.0,
    "PCT POOR": -0.5,
    "PCT FAIR": 0.0,
    "PCT GOOD": 0.5,
    "PCT EXCELLENT": 1.0,
}


Commodities = ["CORN", "WHEAT", "SOYBEANS"]  #list containing key crops

#Retrieving the data
def get_condition_data(commodity:str, year:int, state=None):
    parameters = {
        "key": api_key,
        "source_desc": "SURVEY",
        "commodity_desc": commodity,
        "statisticcat_desc": "CONDITION",
        "agg_level_desc": "NATIONAL",
        "year": str(year),
        "format": "JSON",
    }

    #reformatting the state USDA data
    if state:
        parameters["state_alpha"] = state.upper()

    response = requests.get(Base_URL, params=parameters, timeout=60)
    response.raise_for_status()
    return response.json()["data"]