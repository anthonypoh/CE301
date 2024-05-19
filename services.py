import csv
import glob
import io
import json
import os
import zipfile
import pandas as pd
import requests
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def download(url, destination):
    directory = os.getcwd() + destination

    if not os.path.exists(directory):
        os.makedirs(directory)

    zip_file_path = directory + "/file.zip"

    try:
        response = requests.get(url)
        with open(zip_file_path, "wb") as file:
            file.write(response.content)
        return zip_file_path
    except Exception as e:
        if os.path.exists(zip_file_path):
            return zip_file_path
        else:
            raise Exception(f"Error during download: {str(e)}")


def unzip(zip_file_path, csv_file_pattern):
    try:
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            matching_files = [
                file
                for file in zip_ref.namelist()
                if glob.fnmatch.fnmatch(file, csv_file_pattern)
            ]
            if matching_files:
                csv_file_name = matching_files[0]

                with zip_ref.open(csv_file_name) as csv_file:
                    csv_content = csv_file.read().decode("utf-8")

                    df = pd.read_csv(io.StringIO(csv_content))

                    return df
            else:
                raise Exception("No matching CSV file found in the zip archive")
    except Exception as e:
        raise Exception(f"Failed to unzip file: {str(e)}")


def latest(df):
    try:
        last_5_rows = df.tail(5)
        return last_5_rows
    except Exception as e:
        raise Exception(f"Failed to retrieve the latest rows: {str(e)}")


def predict(df):
    df["bids_received"] = df["bids_received"].str.replace(",", "")
    # Splitting the data into training and testing sets
    X = df.drop(columns=["month", "premium"])
    y = df["premium"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Initialize the linear regression model
    model = LinearRegression()

    # Train the model
    model.fit(X_train, y_train)

    # Predictions on the testing set
    y_pred = model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("Mean Squared Error:", mse)
    print("R-squared:", r2)


# def correlation(df):
#     categories = df["vehicle_class"].unique()
#     latest_month = pd.to_datetime(df["month"].max(), format="%Y-%m")
#     start_month = (latest_month - pd.DateOffset(months=5)).strftime("%Y-%m")
#     filtered_df = df[df["month"] >= start_month]
#     result_dict = {}
#     for category in categories:
#         category_data = filtered_df[filtered_df["vehicle_class"] == category]
#         correlation = category_data["quota"].corr(category_data["premium"])
#         result_dict[category] = correlation

#     return result_dict


# def predict(df, quota, cat):
#     categories = ["A", "B", "C", "D", "E"]
#     if cat not in categories:
#         return "Category does not exist"

#     category = "Category " + cat

#     latest_month = pd.to_datetime(df["month"].max(), format="%Y-%m")
#     start_month = (latest_month - pd.DateOffset(months=2)).strftime("%Y-%m")
#     filtered_df = df[(df["vehicle_class"] == category) & (df["month"] >= start_month)]

#     print(filtered_df)

#     X = filtered_df["quota"].values.reshape(-1, 1)
#     y = filtered_df["premium"].values

#     model = LinearRegression()
#     model.fit(X, y)

#     predicted_premium = model.predict([[quota]])[0]

#     print(
#         f"Predicted premium for {category} with quota {quota} in the last 3 months: {predicted_premium}"
#     )

#     return predicted_premium


# def latest(df):
#     df["bids_received"] = pd.to_numeric(
#         df["bids_received"].str.replace(",", ""), errors="coerce"
#     )
#     return df.tail(5)


# def differences(df):
#     df["bids_received"] = pd.to_numeric(
#         df["bids_received"].str.replace(",", ""), errors="coerce"
#     )

#     last_10_rows = df.tail(10)
#     grouped = last_10_rows.groupby("vehicle_class")
#     differences_dict = {}

#     drop = ["month", "bidding_no"]
#     for category, group in grouped:
#         difference = group.drop(["month", "bidding_no", "vehicle_class"], axis=1).diff()

#         differences_dict[category] = difference.tail(1).to_dict()

#     return differences_dict
