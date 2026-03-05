from clean_week import return_combined_csv
import os
import json

# csv_to_json: convert an existing CSV file to JSON
# Flow: read CSV -> convert to list-of-dicts -> write JSON
def csv_to_json(csv_file, json_file):
    import pandas as pd
    df = pd.read_csv(csv_file)
    data = df.to_dict(orient='records')
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    # Paths used when running this script directly
    # adding a new dir for csv output to keep things organized
    wb_path = os.path.join(os.getcwd(), '2022', '1. JAN', 'B2 Week1 2021-12-27 to 2022-01-02.xlsx')
    csv_file = os.path.join(os.getcwd(), 'output_data', 'combined_data.csv')
    json_file = os.path.join(os.getcwd(), 'output_data', 'combined_data.json')

    # Flow:
    # 1) call return_combined_csv to produce and write the CSV (and get DataFrame back)
    # 2) convert the written CSV to JSON
    df = return_combined_csv(wb_path, csv_file)  # writes CSV and returns DataFrame

    # 3) convert CSV to JSON file
    csv_to_json(csv_file, json_file)