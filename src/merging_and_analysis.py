import os
import sqlite3
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from config import (DB_PATH, DATA_DIR, COMMODITIES, PREDICTORS,
                    PREDICTOR_LABELS, MERGED_JSON, PARTIAL_REGRESSION_JSON, FOREST_PLOT_CSV, COEF_DATA_CSV)
#_______________________________________________
#Load SQLite3 Climate and Crop Yield Data Tables
#_______________________________________________

def run_analysis():
    conn = sqlite3.connect(DB_PATH)
    df_climate = pd.read_sql_query("SELECT * FROM climate", conn)
    df_crop_yield = pd.read_sql_query("SELECT * FROM crop_yield", conn)

    conn.close()

    #Overview of Climate and Crop Yield DataSets
    print("Validating Climate Table")
    print(f"Rows: {len(df_climate)}")
    print(f"Columns: {list(df_climate.columns)}")
    print(f"Years: {df_climate['year'].min()} - {df_climate['year'].max()}")
    print(f"States: {df_climate['state'].unique()}")

    print("Validating Crop Yield Table")
    print(f"Rows: {len(df_crop_yield)}")
    print(f"Columns: {list(df_crop_yield.columns)}")
    print(f"Years: {df_climate['year'].min()} - {df_climate['year'].max()}")
    print(f"States: {df_climate['state'].unique()}")

    #Aggregate climate data from monthly to yearly to match USDA crop yield data

    df_climate_yearly = df_climate.groupby(['state','year']).agg(
        tmax_avg = ('tmax', 'mean'),
        tmin_avg =('tmin', 'mean'),
        tavg_avg =('tavg', 'mean'),
        precip_sum = ('precip', 'sum'),            #calculating annual precipitation
    ).reset_index()

    print(f"The yearly climate data has {len(df_climate_yearly)} rows")
    print(df_climate_yearly.head(), "\n")    #initial look at data

    #Merging the data
    merged = pd.merge(
        df_crop_yield,
        df_climate_yearly,
        on=['state','year'],
        how='inner',
    )

    print(f"Merged rows from dataset joining: {len(merged)}")
    print(merged.head(), "\n")
    print(f"Years: {merged['year'].min()} - {merged['year'].max()}")

    #Check for Missing Data
    null_counts = merged.isnull().sum()
    print(len(null_counts) > 0)

    #Export merged dataset to JSON
    merged_path = os.path.join(DATA_DIR, MERGED_JSON)
    merged.to_json(merged_path, orient='records', indent=2)
    print("Exported to merged_agclimate.json in data folder")

    #____________________
    #Regression Analysis
    #____________________

    df = pd.read_json(merged_path)
    df['commodity'] = df['commodity'].str.title()

    print("Unique commodities in df after title fix:")
    print(df['commodity'].unique())
    print(f"Total rows in df: {len(df)}")

    #Find Difference in Temperature to avoid Multicollinearity
    df['temp_range'] = df['tmax_avg'] - df['tmin_avg']
    df.to_json(merged_path, orient='records', indent=2)  #overrides with temp range variable
    print('Replaced agclimate.json data to add temperature range column')

    #Add Year Effect Variable to Isolate Temperature
    df['year_scaled'] = (df['year'] - df['year'].mean()) / df['year'].std()

    #Adding states as a fixed effect - used AI for fixed effects syntax
    df_model = pd.get_dummies(df, columns=['state'], drop_first=True)
    state_col = [c for c in df_model.columns if c.startswith('state_')]

    OUTCOME = 'yield'

    #Creating the Best-Fit Model per Commodity
    #_________________________________________

    crop_results = {}
    coef_list = []
    forest_plot = []   #list to hold data for visualizations
    partial_records = []

    for COMMODITY in COMMODITIES:

        print(f"\nLooking for: '{COMMODITY}'")
        print(f"Rows matching: {len(df_model[df_model['commodity'] == COMMODITY])}")

        df_crop = df_model[df_model['commodity'] == COMMODITY].dropna(
            subset=PREDICTORS + ['year_scaled'] + state_col + [OUTCOME]
        ).copy()

        #Used AI - Feature Matrix
        continuous_cols = PREDICTORS + ['year_scaled']
        df_crop = df_crop.reset_index(drop=True)
        scaler = StandardScaler()   #want to standardize all predictors into SDs for regression comparability
        df_crop[continuous_cols] = scaler.fit_transform(df_crop[continuous_cols])


        X = df_crop[continuous_cols + state_col]
        Y = df_crop[OUTCOME]

        #Splitting into Training and Testing Data
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

        #Initialize and Train Model
        model = LinearRegression()
        model.fit(X_train, y_train)

        #Regression Output and MSE
        y_pred_test = model.predict(X_test)
        y_pred_train = model.predict(X_train)

        #Regression Test Metrics
        r2_test = r2_score(y_test, y_pred_test)
        mse_test = mean_squared_error(y_test, y_pred_test)
        rmse_test = np.sqrt(mse_test)   #rmse brings value back in bushels/acre

        #Regression Train Metrics
        r2_train = r2_score(y_train, y_pred_train)
        mse_train = mean_squared_error(y_train, y_pred_train)
        rmse_train = np.sqrt(mse_train)

        #Residuals
        residuals = y_test - y_pred_test

        #Used AI to figure out Standard Error - will be used to calculate Confidence Intervals for Forest Plot
        X_train_arr = np.array(X_train, dtype=np.float64)
        XtX_inv = np.linalg.pinv(X_train_arr.T @ X_train_arr)
        se_all = np.sqrt(mse_train * np.diag(XtX_inv))

        #Place Regression Results in Dictionary Per Commodity

        crop_results[COMMODITY] = {
            'model': model,
            'X_test': X_test,
            'y_test': y_test,
            'y_pred': y_pred_test,
            'residuals': residuals,
            'r2_test': r2_test,
            'mse_test': mse_test,
            'rmse_test': rmse_test,
            'r2_train': r2_train,
            'mse_train': mse_train,
            'rmse_train': rmse_train,
            'df_crop': df[df['commodity'] == COMMODITY].dropna(subset=PREDICTORS + [OUTCOME]).copy(),
        }

        df_partial = df[df['commodity'] == COMMODITY].dropna(
            subset=PREDICTORS + ['yield']
        ).copy()

        df_partial['year_scaled'] = (
            (df_partial['year'] - df_partial['year'].mean()) / df_partial['year'].std()
        )

        df_partial = df_partial.rename(columns={'yield': 'crop_yield'})

        model_y = smf.ols('crop_yield ~ C(state) + year_scaled', data=df_partial).fit()
        df_partial['yield_resid'] = model_y.resid

        for pred in PREDICTORS:
            model_x = smf.ols(f'{pred} ~ C(state) + year_scaled', data=df_partial).fit()
            df_partial[f'{pred}_resid'] = model_x.resid

        df_partial['commodity'] = COMMODITY
        partial_records.append(df_partial)

        feature_names = continuous_cols + state_col
        print(f"\n {COMMODITY} ({len(df_crop)} rows")
        print("Training Data")
        print(f"R²:{r2_train:.4f}")
        print(f"MSE:{mse_train:.4f}")
        print(f"RMSE:{rmse_train:.4f}")

        #Used AI to understand how to link together predictor names and coefficients using the zip() function
        print("Now showing climate predictor coefficients...")
        for name, coef in zip(feature_names, model.coef_):
            direction = "↑ higher yield" if coef > 0 else "↓ lower yield"
            print(f"{name} {coef:+.4f} ({direction})")

        #Storing predictor coefficient for coefficient bar chart
        for name, coef in zip(feature_names, model.coef_):
            if name in PREDICTORS:
                coef_list.append({
                    'commodity': COMMODITY,
                    'predictor': PREDICTOR_LABELS[name],
                    'coefficient': coef,
                })

        #Store data for forest plot - forest plot will be used to model accuracy of predictors with CI's
        for name, coef, se in zip(feature_names, model.coef_, se_all):
            if name in PREDICTORS:
                forest_plot.append({
                    'commodity': COMMODITY,
                    'predictor': PREDICTOR_LABELS[name],
                    'coefficient': coef,
                    'se': se,
                    'lower_CI': coef-1.96 * se,
                    'upper_CI': coef+1.96 * se,
                    'r2_test': r2_test,
                    'rmse_test': rmse_test,
                })

    #Regression Output Summary Table
    for COMMODITY, res in crop_results.items():
        print(
            f"Commodity: {COMMODITY}",
            f"Train R²: {res['r2_train']:.4f}",
            f"Train MSE: {res['mse_train']:.4f}",
            f"Train RMSE: {res['rmse_train']:.4f}",
            f"Test R²: {res['r2_test']:.4f}",
            f"Test MSE: {res['mse_test']:.4f}",
            f"Test RMSE: {res['rmse_test']:.4f}",
        )

    #Export coefficient and forest plot data for visualizations
    pd.DataFrame(forest_plot).to_csv(os.path.join(DATA_DIR, FOREST_PLOT_CSV), index=False)
    pd.DataFrame(coef_list).to_csv(os.path.join(DATA_DIR, COEF_DATA_CSV), index=False)

    df_partial_all = pd.concat(partial_records, ignore_index=True)
    df_partial_all.to_json(
        os.path.join(DATA_DIR, PARTIAL_REGRESSION_JSON),
        orient='records', indent=2
    )
    print("Exported partial regression data")







