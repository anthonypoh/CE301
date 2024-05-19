from services import download, unzip
import pandas as pd
import matplotlib.pyplot as plt

LTA_COE_BIDDING_RESULT = "https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle%20Registration/COE%20Bidding%20Results.zip"

# Load data
zip_file_path = download(LTA_COE_BIDDING_RESULT, "/data")
csv_file_pattern = "*-coe_results.csv"

data = unzip(zip_file_path, csv_file_pattern)

# Convert 'month' to datetime and filter years 2014-2024
data['month'] = pd.to_datetime(data['month'])
filtered_data = data[(data['month'].dt.year >= 2014) & (data['month'].dt.year <= 2024)]

# Replace commas and convert 'bids_received' to float using .loc to avoid SettingWithCopyWarning
filtered_data.loc[:, 'bids_received'] = filtered_data['bids_received'].str.replace(',', '').astype(int)

# Plotting COE premiums over time for each vehicle category
categories = filtered_data['vehicle_class'].unique()
plt.figure(figsize=(12, 8))

for category in categories:
    category_data = filtered_data[filtered_data['vehicle_class'] == category]
    plt.plot(category_data['month'], category_data['premium'], label=f'Category {category[-1]}')

plt.title('COE Premium Trends by Vehicle Category (2014-2024)')
plt.xlabel('Year')
plt.ylabel('COE Premium ($)')
plt.legend()
plt.grid(True)
plt.show()
# try:
#     zip_file_path = download(LTA_COE_BIDDING_RESULT, "/data")
#     csv_file_pattern = "*-coe_results.csv"

#     df = unzip(zip_file_path, csv_file_pattern)

#     # Convert the "month" column to datetime format
#     df["month"] = pd.to_datetime(df["month"])

#     # Extract the year from the "month" column
#     df["year"] = df["month"].dt.year

#     # Get the current year
#     current_year = pd.Timestamp.now().year

#     # Filter the DataFrame to include only the last 10 years
#     last_10_years_df = df[df["year"] >= (current_year - 10)]
#     last_10_years_df = last_10_years_df.drop(columns=["year"])

#     catA = last_10_years_df[last_10_years_df["vehicle_class"] == "Category A"]
#     # catA["month"] = last_10_years_df["month"].dt.strftime("%Y-%m")
#     catA["bids_received"] = catA["bids_received"].str.replace(",", "").astype(int)

#     catA_combined = (
#         catA.groupby("month")
#         .agg(
#             {
#                 "quota": "sum",
#                 "bids_success": "sum",
#                 "bids_received": "sum",
#                 "premium": "mean",
#             }
#         )
#         .reset_index()
#     )
# except Exception as e:
#     print(e)
