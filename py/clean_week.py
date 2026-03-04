import pandas as pd 
import openpyxl as op 
import os
# load the file and then read all the sheet MON, TUE, WED, THU, FRI, SAT, SUN AND combine them into one dataframe. AFTER CLEANING THEM 

wb_path = os.path.join(os.getcwd(), '2022', '1. JAN', 'B2 Week1 2021-12-27 to 2022-01-02.xlsx')
def read_excel(file_path):
    df = pd.read_excel(file_path)
    return df

if __name__ == "__main__":
    df = read_excel(wb_path)
    print(df.head())