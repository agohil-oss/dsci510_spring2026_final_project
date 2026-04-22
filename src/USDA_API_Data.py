import requests
import os
import pandas as pd
import json
import matplotlib.pyplot as plt
from config import (DATA_DIR, RESULTS_DIR, USDA_API_BASE_URL, SENTIMENT_SCORES, COMMODITIES, CROP_COLORCODE,
                    SENTIMENT_WEEKLY, SENTIMENT_ANNUAL, SENTIMENT_PLOT_PNG, USDA_API_JSON)

#reading API key - the key.txt file must be in the same folder

def sentiment_analysis():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    #Load USDA API Key
    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(base_dir, 'key.txt'), 'r') as f:
            api_key = f.read().strip()
            print(f"Key: {api_key}")
    except FileNotFoundError:
        raise FileNotFoundError("No API key found.")

    #retrieving USDA data via webscraping
    def get_condition_data(commodity: str, year: int, state=None):
        parameters = {
            "key":               api_key,
            "source_desc":       "SURVEY",
            "commodity_desc":    commodity,
            "statisticcat_desc": "CONDITION",
            "agg_level_desc":    "NATIONAL",
            "year":              str(year),
            "format":            "JSON",
        }
        if state:
            parameters["state_alpha"] = state.upper()
        response = requests.get(USDA_API_BASE_URL, params=parameters, timeout=60)
        response.raise_for_status()
        return response.json()["data"]

    YEARS = list(range(2010,2026))
    all_records = []

    for commodity in COMMODITIES:
        for year in YEARS:
            records = get_condition_data(commodity.upper(), year)
            all_records.extend(records)

    api_output_path = os.path.join(DATA_DIR, USDA_API_JSON)
    with open(api_output_path, 'w') as f:
        json.dump(all_records, f)
    print(f"Total records loaded: {len(all_records)}")

    #use pandas to read it and use pandas.drop na command and clean the dataset
    records = []

    #Used AI to help with reading the JSON file since it was not in typical format. Now reading line by line
    with open(api_output_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)

                if isinstance(obj, dict) and 'data' in obj:
                    records.extend(obj['data'])
                elif isinstance(obj, list):
                    records.extend(obj)
                else:
                    records.append(obj)
            except json.JSONDecodeError:
                continue

    print(f"Total records loaded: {len(records)}")
    df = pd.json_normalize(records)
    df['commodity_desc'] = df['commodity_desc'].str.title()
    print(df.head())

    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')      #converting the atyipcal values into null
    df.dropna(subset =['Value'], inplace=True)  #dropping any rows with null values in the dataset

    #Restructure data for sentiment analysis
    df = df[['commodity_desc', 'year', 'week_ending', 'short_desc', 'Value']].copy()

    print(df.head())

    #Setting up data with sentiment score range

    def sentiment_weight(short_desc):
        for scale, weight in SENTIMENT_SCORES.items():
            if scale in short_desc:
                return weight
        return None

    df['sentiment_weight'] = df['short_desc'].apply(sentiment_weight)
    df = df.dropna(subset=['sentiment_weight'])

    print(f"\nRows with sentiment weights: {len(df)}")
    print(df[['short_desc', 'sentiment_weight']].drop_duplicates())

    #Calculate the sentiment weight
    df['weighted_score'] = (df['Value'] * df['sentiment_weight'] / 100)

    #Need to convert weekly data to datetime for plotting it
    sentiment_weekly = df.groupby(
        ['commodity_desc', 'year', 'week_ending']
    )['weighted_score'].sum().reset_index()

    sentiment_weekly.columns = ['commodity', 'year', 'week_ending', 'sentiment_score']

    sentiment_weekly['week_ending'] = pd.to_datetime(sentiment_weekly['week_ending'])
    print(sentiment_weekly.head())

    #Aggreate to annual sentiment scores
    sentiment_annual = sentiment_weekly.groupby(
        ['commodity', 'year',]
    )['sentiment_score'].mean().reset_index()

    print(f"Annual Average Sentiment {sentiment_annual.to_string(index=False)}")

    #Export Results
    sentiment_weekly.to_csv(os.path.join(DATA_DIR, SENTIMENT_WEEKLY), index=False)
    sentiment_annual.to_csv(os.path.join(DATA_DIR, SENTIMENT_ANNUAL), index=False)
    print("Exported both weekly and annual sentiment scores for commodities")

    #Visualization
    fig, ax = plt.subplots(figsize=(11,5))

    for commodity in COMMODITIES:
        df_plot = sentiment_annual[sentiment_annual['commodity'] == commodity]
        color = CROP_COLORCODE.get(commodity, 'grey')

        ax.plot(
            df_plot['year'],
            df_plot['sentiment_score'],
            marker='o',
            label=commodity,
            color=color,
            linewidth=2,
        )

    #Reference line
    ax.axhline(0, color='black', linewidth=1, linestyle='--', alpha=0.5)

    ax.set_xlabel("Year", fontsize=14)
    ax.set_ylabel("Sentiment Score\n(-1 = Very Poor -> +1 = Excellent)", fontsize=10)
    ax.set_title(
        "Annual Crop Condition Sentiment Score (USDA)\n"
        "Weighted average of reported condition categories",
        fontsize=12, fontweight='bold',
    )

    ax.legend(title='Commodity')
    ax.grid(True, linestyle='-', alpha=0.3)

    plt.tight_layout()

    #Exporting the sentiment analysis plot

    plt.savefig(os.path.join(RESULTS_DIR, SENTIMENT_PLOT_PNG), dpi=150)
    plt.close()
    print(f"Saved sentiment plot to results folder!")

