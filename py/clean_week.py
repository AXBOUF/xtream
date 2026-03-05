import pandas as pd
import openpyxl as op
import os

wb_path = os.path.join(os.getcwd(), '2022', '1. JAN', 'B2 Week1 2021-12-27 to 2022-01-02.xlsx')

def clean_data(df, sheet_name=None):
    df = df[pd.to_numeric(df['Docket No'], errors='coerce').notnull()].copy()
    df = df.reset_index(drop=True)
    df = df.iloc[:, :15]
    df['Docket No'] = df['Docket No'].astype(int)
    if sheet_name:
        df.insert(0, 'Day', sheet_name)  # tag rows with sheet/day name
    return df

def combine_sheets(file_path):
    wb = op.load_workbook(file_path)
    sheet_names = wb.sheetnames[:-1]  # exclude summary sheet
    frames = []
    for sheet in sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet, header=3)
        cleaned = clean_data(df, sheet_name=sheet)
        frames.append(cleaned)
    return pd.concat(frames, ignore_index=True)

if __name__ == "__main__":
    combined_df = combine_sheets(wb_path)
    print(combined_df)
    print(f"\nShape: {combined_df.shape}")
    print(f"Days found: {combined_df['Day'].unique()}")