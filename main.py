from flask import Flask, jsonify
import os
from services import download, unzip, latest, predict
import matplotlib.pyplot as plt
import pandas as pd

app = Flask(__name__)

LTA_COE_BIDDING_RESULT = "https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle%20Registration/COE%20Bidding%20Results.zip"
directory = os.getcwd()


@app.route("/")
def index():
    try:
        zip_file_path = download(LTA_COE_BIDDING_RESULT, "/data")
        csv_file_pattern = "*-coe_results.csv"

        df = unzip(zip_file_path, csv_file_pattern)

        # Convert the "month" column to datetime format
        df["month"] = pd.to_datetime(df["month"])

        # Extract the year from the "month" column
        df["year"] = df["month"].dt.year

        # Get the current year
        current_year = pd.Timestamp.now().year

        # Filter the DataFrame to include only the last 10 years
        last_10_years_df = df[df["year"] >= (current_year - 10)]
        last_10_years_df = last_10_years_df.drop(columns=["year"])

        catA = last_10_years_df[last_10_years_df["vehicle_class"] == "Category A"]
        catA["month"] = last_10_years_df["month"].dt.strftime("%Y-%m")
        catA['bids_received'] = catA['bids_received'].str.replace(',', '').astype(int)

        # Group by "month" and aggregate premiums by taking their mean
        catA_combined = (
            catA.groupby("month")
            .agg(
                {
                    "quota": "sum",
                    "bids_success": "sum",
                    "bids_received": "sum",
                    "premium": "mean",  # Taking the mean of premiums for bidding 1 and 2
                }
            )
            .reset_index()
        )
        # catA = catA.groupby(['month', 'vehicle_class']).sum().reset_index()

        return catA_combined.to_json(orient="records")
        # return df.to_json(orient="records")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get-difference")
def getDifference():
    zip_file_path = directory + "/data/file.zip"
    csv_file_pattern = "*-coe_results.csv"

    download(LTA_COE_BIDDING_RESULT, "/data")
    df = unzip(zip_file_path, csv_file_pattern)

    difference = differences(df)
    return jsonify(difference=difference)


@app.route("/api/get-prediction/<int:quota>/<string:cat>", methods=["GET"])
def getPrediction(quota, cat):
    zip_file_path = directory + "/data/file.zip"
    csv_file_pattern = "*-coe_results.csv"

    download(LTA_COE_BIDDING_RESULT, "/data")
    df = unzip(zip_file_path, csv_file_pattern)

    prediction = predict(df, quota, cat)

    return jsonify(quota=quota, category=cat, prediction=prediction)


@app.route("/api/get-correlation", methods=["GET"])
def getCorrelation():
    zip_file_path = directory + "/data/file.zip"
    csv_file_pattern = "*-coe_results.csv"

    download(LTA_COE_BIDDING_RESULT, "/data")
    df = unzip(zip_file_path, csv_file_pattern)

    corr = correlation(df)

    return jsonify(correlation=corr)


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
