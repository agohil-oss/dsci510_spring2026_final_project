this is my README

Project: USDA Agricultural Crop Yield Project (Corn, Soy, Wheat) by Core Climate Predictors from 2010-2025

**Introduction**
This project is doing a multivariate regression analysis on crop yield (measured in bushels/acre) for three key crops in the United States - corn, wheat, and soybeans - based on fluctuations 
in climate over the past 15 years. The first data source is the USDA National Agricultural Statistics that retrieved data on commodities and their corresponding yearly crop yield
value in all states. The second data source used the NOAA Climate Division Set to retrieve annual climate data on mean high, low, and average temperature and total precipitation levels.
It also includes a sentiment analysis on USDA crop condition rated by farmers from the past 15 years.

**Data Sources**
| Data Source | Description | Source URL | Type | List of Fields | Format | Estimated Data Size After Cleaning |
|---|---|---|---|---|---|---|
| USDA National Agricultural Statistics Service (NASS) | Used USDA Crop Quick Statistics tool with variable parameters for crop type, annual crop yield, state, year | [USDA QuickStats](https://quickstats.nass.usda.gov/results/3629F1BB-CAEF-30D9-9F97-5AAB51E90C76) | File | Year, State, Commodity (Corn, Wheat, Soybean), Yield Value (Bushels/Acre) | CSV | After locating relevant fields for the model, there are **601 rows of data** |
| NOAA U.S. Climate Grid Dataset | Will utilize the NOAA dataset to access real-time temperature and precipitation data | [NOAA Climate Division](https://www.ncei.noaa.gov/pub/data/cirs/climdiv/) | File | Year, State, Average Temperature, Mean Max Temperature, Mean Min Temperature, Average Precipitation Level | TXT | After locating relevant fields for the model, there are **601 rows of data** |
| USDA NASS Crop Condition/Progress | Will pull data from the past 15 years on farmer's crop condition ratings for sentiment analysis | [USDA QuickStats API](https://quickstats.nass.usda.gov/api) | API/Web Scraping | Crop Condition Score, State, Year, Commodity (Corn, Wheat, Soybean) | JSON | Weekly sentiment score per commodity (3) for 15 years; data size is **5,823 rows** |

**Analysis**
This project conducts a multivariate regression using USDA crop yield data and NOAA climate data annually over the past 15 years.
This project also conducts a sentiment analysis using USDA Crop Condition ratings via USDA API Key/ Web Scraping

**Overall Project Structure**

dsci510_spring2026_final_project/
├── data/              # Gets auto-populated when running main.py
├── results/           # Gets auto-populated when running main.py
├── src/
│   ├── database_creation.py
│   ├── USDA_API_Data.py
│   ├── merging_and_analysis.py
│   ├── visualizations.py
│   └── main.py
├── docs/
│   ├── Avani_Gohil_presentation.pdf
│   ├── Avani_Gohil_Progress_Report.pdf
├── config.py
├── tests.py
├── results.ipynb
├── requirements.txt
├── .env.example
└── README.md

**Requirements**
- Python 3.10+
  
*Install dependencies with....*

pip install -r requirements.txt

**API Key Setup (Required to do before running)**

1. Get a free USDA API Key at: https://quickstats.nass.usda.gov/api
2. In the project root directory, copy '.env.example' to a new file called '.env':
For Mac → cp .env.example .env 
For Windows → copy .env.example .env
3. Open .env file and paste API key inside: USDA_API_KEY="paste your API key here".


**Running the Project**

DO THIS IN ORDER! 

1. Clone the repository -> git clone <repo_url> 
                           cd dsci510_spring2026_final_project
2. Install dependencies as specified before
3. Add USDA API Key as specified before
4. Run the full project pipeline from main.py → python src/main.py

What will happen...
- NOAA climate data will be downloaded in data folder
- USDA crop yield data CSV will be automatically downloaded from Google Drive
- Merge NOAA and USDA Data Tables into JSON file - basis for running regression analysis
- For sentiment analysis, will fetch USDA crop condition data via API
- Run sentiment analysis on crop condition data are rescaling to sentiment score ranges
- And finally, create and save all chart visualizations to the results folder

5. After running the project, run tests.py to verify everything worked → python tests.py 
6. View visualizations in Jupyter notebook → jupyter notebook results.ipynb

*all commands must be run from the project root directory (dsci510_spring2026_final_project/)

**Results**
After running main.py, the following files will be in the results/ folder:
- sentiment_plot.png — Annual crop condition sentiment scores (2010-2025)
- forest_plot.png — Effect size plot of climate predictors on crop yield
- faceted_regression_plot.png — Partial regression plots by commodity
Narrative Results
- Corn is a highly sensitive crop - temperature volatility has higher effect for corn and wheat while soy is more climate resilient
- Standardized coefficient for annual total precipitation is negative for all crops; may signal effect of flooding over past decade
- Higher precipitation fall has stronger negative coefficient for wheat
- Corn and Soybeans has negative sentiment score in 2012, aligning with corn and soy belt region droughts during that time

*notes - Claude AI was used to help out with code with analyses - multivariate regressions (and subsequent charts) and how to structure visualizations. I also used Gemini
to help with understanding proper code for web scraping.*

