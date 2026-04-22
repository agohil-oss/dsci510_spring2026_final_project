#USDA API Web Scraping for Sentiment Analysis
import json
from src.USDA_API_Data import get_condition_data, Commodities

if __name__ == "__main__":

    with open('../USDA_API_Data.json', 'w') as outfile:
        # creating for loop to retrieving data for 3 main commodities
        for crop in Commodities:
            for year in range(2015, 2026):
                rows = get_condition_data(crop, year)
                for row in rows:
                    row['crop'] = crop
                    row['year'] = year
                    outfile.write(json.dumps(row) + "\n")
                print(f"{crop} {year}: {len(rows)} rows")

    print("USDA_API_Data.json was saved successfully")

