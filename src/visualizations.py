import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches
import os
from config import (DATA_DIR, RESULTS_DIR, COMMODITIES, PREDICTOR_LABELS, CROP_COLORCODE, FOREST_PLOT_CSV,
                    FOREST_PLOT_PNG, FACETED_PLOT_PNG, PARTIAL_REGRESSION_JSON, MERGED_JSON)


def visualizations():

    input_forest_data = os.path.join(DATA_DIR, FOREST_PLOT_CSV)
    input_raw_data = os.path.join(DATA_DIR, MERGED_JSON)
    input_partial_data = os.path.join(DATA_DIR, PARTIAL_REGRESSION_JSON)


    data = {
        'forest': pd.read_csv(input_forest_data),
        'raw_data': pd.read_json(input_raw_data),
        'partial': pd.read_json(input_partial_data)
    }

    PREDICTOR = ['tavg_avg', 'temp_range', 'precip_sum']

    #________________________________
    #Forest/Coefficient Plot with Crop Subgroups
    #________________________________
    df_forest = data['forest']
    predictors = df_forest['predictor'].unique()

    #Building the Forest /Coefficient Plot
    fig, ax = plt.subplots(figsize=(10,6))
    crop_gap = 0.25
    predictor_gap = 1.2
    y_pos = 0
    yticks = []
    yticklabels = []

    #Looping through predictors and commodities

    for predictor in predictors:
        df_pred = df_forest[df_forest['predictor'] == predictor]

        for i, COMMODITY in enumerate(COMMODITIES):
            row = df_pred[df_pred['commodity'] == COMMODITY]
            if row.empty:
                continue

            coef = row['coefficient'].values[0]
            lower_CI = row['lower_CI'].values[0]
            upper_CI = row['upper_CI'].values[0]
            color = CROP_COLORCODE[COMMODITY]
            r2 = row['r2_test'].values[0]

            #Creating the Confidence Interval - Used AI to help with formatting code
            ax.plot([lower_CI, upper_CI], [y_pos, y_pos], color=color, linewidth=2, alpha=0.7)

            #Coefficient Dot
            ax.scatter(coef, y_pos, color=color, s=80, zorder=3)

            #Labeling the R2 Score
            ax.text(upper_CI + 0.5, y_pos, f"R²={r2:.2f}", va='center', fontsize=7.5, color=color)

            yticks.append(y_pos)
            yticklabels.append(COMMODITY)

            y_pos -= crop_gap

        ax.text(-2.8, y_pos -0.1, predictor, fontsize=9, fontweight='bold', va='center')

        #Formatting
        ax.axhline(y_pos - crop_gap * 0.3, color='lightgrey', linewidth= 0.8)
        y_pos -= predictor_gap

    #Vertical Line for Forest Plot
    ax.axvline(0, color='black', linewidth = 1.1, linestyle='--', alpha=0.7)

    #Y-Axis Ticks and Crop Labels
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels, fontsize=9)

    ax.set_xlabel('Coefficient (standardized) | Error Bars (95% CI)', fontsize=10)
    ax.set_title(
        "Effect Size Plot - Climate Predictors on Crop Yield\n"
        "Controlling for State Fixed Effects and Year Trends",
        fontsize=12, fontweight='bold',
    )

    #Used AI to help with formatting plot
    handles = [mpatches.Patch(color=CROP_COLORCODE[c], label=c) for c in COMMODITIES]
    ax.legend(handles=handles, title='Commodity', fontsize=9)

    ax.grid(True, linestyle='--', alpha=0.3, axis='x')
    ax.set_xlim(left=-15.0, right=15)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, FOREST_PLOT_PNG), dpi=150, bbox_inches='tight')
    plt.show()
    plt.close()
    print(f"Saved → {os.path.join(RESULTS_DIR, FOREST_PLOT_PNG)}")


    #________________________________
    #Partial Regression Plot with Crop Subgroups
    #________________________________

    df_partial = data['partial']

    num_rows = len(PREDICTOR)
    num_cols = len(COMMODITIES)

    #Used AI for Regression Plot Formatting
    fig,axes = plt.subplots(num_rows, num_cols, figsize=(14,11), sharex='row')

    fig.suptitle(
        "Crop Yield Measured by Climate Indicators (2010-2025)",
        fontsize=12, fontweight='bold',
    )

    #Loop through all data through rows and columns
    for value, predictor in enumerate(PREDICTOR):
        for i, COMMODITY in enumerate(COMMODITIES):

            ax = axes[value][i]
            color = CROP_COLORCODE[COMMODITY]

            df_plot = df_partial[df_partial['commodity'] == COMMODITY].dropna(
                subset=[f'{predictor}_resid', 'yield_resid'])

            #Regression Line
            sns.regplot(
                data=df_plot,
                x=f'{predictor}_resid',
                y='yield_resid',
                ax=ax,
                color=color,
                scatter_kws={'alpha': 0.3, 's': 18},
                line_kws={'linewidth':2},
                ci=None
            )


            if value == 0:
                ax.set_title(COMMODITY, fontsize=11, fontweight='bold', color=color)


            ax.set_xlabel(f"{PREDICTOR_LABELS[predictor]}\n(residual)", fontsize=9)

            if i ==0:
                ax.set_ylabel("Yield Residual\n(bushels/acre)", fontsize=9)
            else:
                ax.set_ylabel("")

            ax.grid(True, linestyle='--', alpha=0.25)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, FACETED_PLOT_PNG), dpi=150, bbox_inches='tight')
    plt.show()
    plt.close()
    print("Saved faceted regression plot in results!")

