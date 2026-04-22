#Python Script that runs all code from start to finish

from src.database_creation import build_database
from src.merging_and_analysis import run_analysis
from src.visualizations import visualizations
from src.USDA_API_Data import sentiment_analysis

if __name__ == "__main__":

    print("\n Step 1: Building the Agclimate Database")
    build_database()

    print("\n Step 2: Merging USDA and NOAA Data and Running Regression Analysis")
    run_analysis()

    print("\n Step 3: Visualizations of Forest/Effect Size Plot and Faceted Regression Plots")
    visualizations()

    print("\n Step 4: USDA Sentiment Analysis on Crop Conditions")
    sentiment_analysis()

    print("Project fully executed successfully!")