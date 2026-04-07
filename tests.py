#USDA API Web Scraping for Sentiment Analysis
import json

from USDA_API_Data import get_condition_data, Commodities

if __name__ == "__main__":

    USDA_data = {}
    # creating for loop to retrieving data for 3 main commodities
    for crop in Commodities:
        USDA_data[crop] = []
        for year in range(2015, 2026):
            rows = get_condition_data(crop, year)
            USDA_data[crop].extend(rows)
            print(f"{crop} {year}: {len(rows)} rows")

    with open('USDA_API_Data.json', 'w') as outfile:
        json.dump(USDA_data, outfile, indent=2)

    print("USDA_API_Data.json was saved successfully")

