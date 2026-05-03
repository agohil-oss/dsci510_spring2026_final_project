import os

#Directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
RESULTS_DIR = os.path.join(ROOT_DIR, "results")
SRC_DIR = os.path.join(ROOT_DIR, "src")

#Database
DB_NAME = 'agclimate.db'
DB_PATH = os.path.join(DATA_DIR, DB_NAME)

#Data Files
USDA_CSV = "USDA Crop Yield_Dataset_Raw.csv"
USDA_GDRIVE_ID = "1hOY77lRu1WS0qtkt2-7L4TzVW0npjma-"
MERGED_JSON = "merged_agclimate.json"
FOREST_PLOT_CSV = "forest_plot.csv"
COEF_DATA_CSV = "coef_data.csv"
SENTIMENT_WEEKLY = "sentiment_weekly.csv"
SENTIMENT_ANNUAL = "sentiment_annual.csv"
USDA_API_JSON = "USDA_API_Data.json"
PARTIAL_REGRESSION_JSON = "partial_regression.json"

#NOAA Data Retrieval
NOAA_BASE_URL = "https://www.ncei.noaa.gov/pub/data/cirs/climdiv/"

#USDA API
USDA_API_BASE_URL = "https://quickstats.nass.usda.gov/api/api_GET/"

# Regression/Sentiment Analysis Parameters
COMMODITIES = ['Corn', 'Soybeans', 'Wheat']

PREDICTORS = ['temp_range', 'tavg_avg', 'precip_sum']

PREDICTOR_LABELS = {
    'tavg_avg':   'Avg Mean Temperature (°F)',
    'temp_range': 'Avg Temperature Range / Temperature Volatility (°F)',
    'precip_sum': 'Total Annual Precipitation (in.)',
}

CROP_COLORCODE = {
    'Corn':     'darkorange',
    'Soybeans': 'seagreen',
    'Wheat':    'steelblue',
}

#Sentiment Score Scale
SENTIMENT_SCORES = {
    "PCT VERY POOR": -1.0,
    "PCT POOR":      -0.5,
    "PCT FAIR":       0.0,
    "PCT GOOD":       0.5,
    "PCT EXCELLENT":  1.0,
}

# Result Files
FOREST_PLOT_PNG         = "forest_plot.png"
FACETED_PLOT_PNG        = "faceted_regression_plot.png"
SENTIMENT_PLOT_PNG      = "USDA_sentiment_plot.png"


