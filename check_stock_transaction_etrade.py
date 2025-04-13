import os
import argparse
import datetime
import pandas as pd
from common.headers import ETRADE_HEADER


DEBUG = False

EXRATE_DICT = {
    "01/31/2024": 1330.60,
    "02/20/2024": 1333.80,
    "02/21/2024": 1337.90,
    "03/07/2024": 1335.70,
    "05/20/2024": 1355.20,
    "05/21/2024": 1356.20,
    "08/20/2024": 1337.80,
    "08/21/2024": 1332.00,
}


def add_KRW_info(file_path: str, output_path: str) -> None:
    """Adds KRW-based columns to the given Excel file."""

    # Read Excel file
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")
    df_raw = pd.read_excel(file_path, sheet_name="G&L_Collapsed")

    # Filter out empty rows and ensure consistent column names
    df = df_raw.dropna(axis=0, how="any")
    df = df.reindex(columns=ETRADE_HEADER, fill_value=None)

    # Fetch historical KRW exchange rates from the EXRATE_DICT (by hands)
    # TODO: Replace with an automatic solution using webpage crawling from url = "http://www.smbs.biz/ExRate/TodayExRate.jsp"
    dates = list(set(df["Date Acquired"].tolist() + df["Date Sold"].tolist()))
    dates.sort()
    for date in dates:
        if date in EXRATE_DICT.keys():
            continue
        date_obj = datetime.datetime.strptime(date, "%m/%d/%Y")
        date_new = date_obj.strftime("%Y%m%d")
        print(date, date_new)
        raise AssertionError(f"Date {date} not found in EXRATE_DICT")

    # Update KRW-based columns
    for i, row in df.iterrows():
        date = row["Date Acquired"]
        exrate = get_exrate(date)
        df.loc[i, "ER Date Acquired (KRW)"] = exrate
        df.loc[i, "Adjusted Cost Basis (KRW)"] = row["Adjusted Cost Basis"] * exrate

        date = row["Date Sold"]
        exrate = get_exrate(date)
        df.loc[i, "ER Date Sold (KRW)"] = exrate
        df.loc[i, "Total Proceeds (KRW)"] = row["Total Proceeds"] * exrate
        gain_krw = (
            df.loc[i, "Total Proceeds (KRW)"] - df.loc[i, "Adjusted Cost Basis (KRW)"]
        )
        df.loc[i, "Adjusted Gain/Loss (KRW)"] = gain_krw

    # Calculate total gain/loss (USD and KRW)
    print_gain_tax(df["Adjusted Gain/Loss"].sum(), df["Adjusted Gain/Loss (KRW)"].sum())

    # Save to CSV
    df.to_csv(output_path, index=False)


def get_exrate(date: str) -> float:
    """Fetches the exchange rate for a given date."""

    if date in EXRATE_DICT:
        return EXRATE_DICT[date]
    else:
        raise AssertionError(f"Date {date} not found in EXRATE_DICT")


def print_gain_tax(total_gain_loss: float, total_gain_loss_krw: float) -> None:

    print("-"*37)
    print("Total Gain/Loss:" + f"{total_gain_loss:,.2f} USD".rjust(20))
    print("Total Gain/Loss:" + f"{round(total_gain_loss_krw):,} KRW".rjust(20))
    print("-"*37)


def parse_args():
    """Parses command-line arguments for file paths."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-path", type=str, required=True)
    parser.add_argument("--output-path", type=str, required=True)
    args = parser.parse_args()

    return args


if __name__ == "__main__":

    if DEBUG:
        # In debug mode, use a specific file and year
        year = 2024
        base_dir = f"{year}"
        file_path = f"{base_dir}/{year}_G&L_Collapsed.xlsx"
        output_path = f"{base_dir}/{year}_etrade.csv"
        add_KRW_info(file_path, output_path)
    else:
        args = parse_args()
        add_KRW_info(args.file_path, args.output_path)
