import pandas as pd
import openpyxl as op
import os
import glob
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),                          # print to terminal
        logging.FileHandler('output_data/process.log')   # also write to file
    ]
)

def get_file_paths():
    return glob.glob(os.path.join(os.getcwd(), '2022', '**', '*.xlsx'), recursive=True)

def clean_data(df, sheet_name=None):
    df = df[pd.to_numeric(df['Docket No'], errors='coerce').notnull()].copy()
    df = df.reset_index(drop=True)
    df = df.iloc[:, :15]
    df['Docket No'] = df['Docket No'].astype(int)
    if sheet_name:
        df.insert(0, 'Day', sheet_name)
    return df

def combine_sheets(file_path):
    wb = op.load_workbook(file_path)
    frames = []
    for sheet in wb.sheetnames[:-1]:
        try:
            df = pd.read_excel(file_path, sheet_name=sheet, header=3)
            frames.append(clean_data(df, sheet_name=sheet))
            logging.info(f"OK       {file_path} | sheet: {sheet}")
        except Exception as e:
            logging.warning(f"SKIPPED  {file_path} | sheet: {sheet} | reason: {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def export(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    all_frames = []
    files = get_file_paths()
    logging.info(f"Found {len(files)} files")
    for f in files:
        try:
            all_frames.append(combine_sheets(f))
            logging.info(f"DONE     {f}")
        except Exception as e:
            logging.error(f"FAILED   {f} | reason: {e}")
    df = pd.concat(all_frames, ignore_index=True)
    df.to_csv(os.path.join(output_dir, 'combined_data.csv'), index=False)
    logging.info(f"Exported {len(df)} rows to combined_data.csv")
    return df

if __name__ == "__main__":
    df = export(os.path.join(os.getcwd(), 'output_data'))
    print(df)
    print(f"\nShape: {df.shape}")
    print(f"Days found: {df['Day'].unique()}")
