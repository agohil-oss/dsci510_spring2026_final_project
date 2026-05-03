import sqlite3
import os
import pandas as pd

from src.database_creation import create_tables
from config import DB_PATH, DATA_DIR, USDA_CSV, MERGED_JSON, SENTIMENT_WEEKLY, SENTIMENT_ANNUAL, COMMODITIES

#Used AI to figure out assert commands can help validate data loading in a tests.py file
def test_tables():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    create_tables(cur)

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]

    assert "crop_yield" in tables, "crop_yield table was not found in tables"
    assert "climate" in tables, "climate table was not found in tables"
    conn.close()
    print("Passed: Both tables created!")

def test_load_usda_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM crop_yield")
    count = cur.fetchone()[0]

    assert count > 0, "crop_yield table empty"
    conn.close()
    print(f"PASS: crop_yield has {count} rows")

def test_load_NOAA_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM climate")
    count = cur.fetchone()[0]

    assert count > 0, "climate table empty"
    conn.close()
    print(f"PASS: climate table has {count} rows")

# climate table loads from database and now Dataframe
def test_climate_data_loads():
    conn = sqlite3.connect(DB_PATH)
    df_climate = pd.read_sql_query("SELECT * FROM climate", conn)
    conn.close()

    assert isinstance(df_climate, pd.DataFrame), "Climate data should be a dataframe"
    assert not df_climate.empty, "Climate table should not be empty"
    print(f"PASS: Climate table loaded with {len(df_climate)} rows")

#crop_yield table loads from database and now Dataframe
def test_crop_yield_data_loads():
    conn = sqlite3.connect(DB_PATH)
    df_crop_yield = pd.read_sql_query("SELECT * FROM crop_yield", conn)
    conn.close()

    assert isinstance(df_crop_yield, pd.DataFrame), "Crop yield data should be a dataframe"
    assert not df_crop_yield.empty, "Crop yield table should not be empty"
    print(f"PASS: Crop yield table loaded with {len(df_crop_yield)} rows")

# checking if merged JSON file exists after export
def test_merged_json_exists():
    merged_path = os.path.join(DATA_DIR, MERGED_JSON)
    assert os.path.exists(merged_path), "Merged JSON file was not created"
    print("PASS: Merged JSON file exists")

#merged JSON loads correctly with right amount of rows
def test_merged_data_has_expected_columns():
    merged_path = os.path.join(DATA_DIR, MERGED_JSON)
    df = pd.read_json(merged_path)

    expected_columns = ["state", "year", "commodity", "yield", "tmax_avg", "tmin_avg", "tavg_avg", "precip_sum"]
    for col in expected_columns:
        assert col in df.columns, f"Missing column '{col}' in merged data"
    print("PASS: Merged data has all expected columns")

def test_sentiment_weekly_loads():
    path = os.path.join(DATA_DIR, SENTIMENT_WEEKLY)
    assert os.path.exists(path), "Sentiment weekly data file was not created"

    df = pd.read_csv(path)
    assert not df.empty, "Weekly sentiment data should not be empty"
    assert "commodity" in df.columns, "missing 'commodity' column"
    assert "sentiment_score" in df.columns, "missing 'sentiment_score' column"
    print(f"PASS: Sentiment weekly data loaded with {len(df)} rows")

def test_sentiment_annual_loads():
    path = os.path.join(DATA_DIR, SENTIMENT_ANNUAL)
    assert os.path.exists(path), "Sentiment annual data file was not created"

    df = pd.read_csv(path)
    assert not df.empty,"Annual sentiment data should not be empty"
    assert "commodity" in df.columns, "missing 'commodity' column"
    assert "sentiment_score" in df.columns, "missing 'sentiment_score' column"
    print(f"PASS: Sentiment annual data loaded with {len(df)} rows")

def test_sentiment_commodities():
    path = os.path.join(DATA_DIR, SENTIMENT_ANNUAL)
    df = pd.read_csv(path)

    for commodity in COMMODITIES:
        assert commodity in df['commodity'].values, f"Missing commodity '{commodity}' in sentiment data"
    print("PASS: Sentiment commodities loaded")

def test_sentimentscore_range():
    path = os.path.join(DATA_DIR, SENTIMENT_ANNUAL)
    df = pd.read_csv(path)

    assert df['sentiment_score'].between(-1,1).all(), "Sentiment score range should be between -1 and 1"
    print("PASS: Sentiment score range is valid")

#Running Tests
if __name__ == "__main__":
    print("Running tests for all data loads...")
    #Tests for database_creation.py
    test_tables()
    test_load_usda_data()
    test_load_NOAA_data()

    #Tests for merging_and_analysis.py
    test_climate_data_loads()
    test_crop_yield_data_loads()
    test_merged_json_exists()
    test_merged_data_has_expected_columns()

    #Tests for USDA_API_Data.py
    test_sentiment_annual_loads()
    test_sentiment_weekly_loads()
    test_sentiment_commodities()
    test_sentimentscore_range()

    print("All tests passed!")
