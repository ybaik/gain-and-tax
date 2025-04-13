import os
import json
import argparse
import datetime
import pandas as pd
from pathlib import Path
from common.headers import ETRADE_HEADER
from common.crawler import Crawler


DEBUG = False

usd_krw_db_path = Path("./db/usd_krw.json")


def add_KRW_info(file_path: str, output_path: str, use_crawling: bool) -> None:
    """Adds KRW-based columns to the given Excel file."""

    # Initialize crawler
    if use_crawling:
        print("Using web crawling to get transaction data...")
        crawler = Crawler(headless=True)

    # Read USD-KRW exchange rate DB
    if usd_krw_db_path.exists():
        with open(usd_krw_db_path) as f:
            USD_KRW_DB = json.load(f)
    else:
        USD_KRW_DB = dict()

    # Read Excel file
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")
    df_raw = pd.read_excel(file_path, sheet_name="G&L_Collapsed")

    # Filter out empty rows and ensure consistent column names
    df = df_raw.dropna(axis=0, how="any")
    df = df.reindex(columns=ETRADE_HEADER, fill_value=None)

    # Fetch historical KRW exchange rates from the USD_KRW_DB (by hands or web crawling)
    # An automatic solution using webpage crawling from url = "http://www.smbs.biz/ExRate/TodayExRate.jsp"
    dates = list(set(df["Date Acquired"].tolist() + df["Date Sold"].tolist()))
    dates.sort()
    for date in dates:
        if date in USD_KRW_DB.keys():
            continue

        date_obj = datetime.datetime.strptime(date, "%m/%d/%Y")
        date_new = date_obj.strftime("%Y%m%d")

        if use_crawling:
            crawler.open_page("http://www.smbs.biz/ExRate/TodayExRate.jsp")
            exkrw = crawler.get_USD_KRW_rate(date_new)
            if exkrw is not None:
                print(f"*** Date {date} is crawled and added to USD_KRW_DB")
                USD_KRW_DB[date] = exkrw
                continue

        print(date, date_new)
        raise AssertionError(f"Date {date} not found in USD_KRW_DB")

    if use_crawling:
        crawler.deinit()

    # Save the USD-KRW exchange rate DB with sorting
    USD_KRW_DB = dict(sorted(USD_KRW_DB.items()))
    with open(usd_krw_db_path, "w") as f:
        json.dump(USD_KRW_DB, f, indent=4)

    # Update KRW-based columns
    for i, row in df.iterrows():
        date = row["Date Acquired"]
        exrate = get_exrate(date, USD_KRW_DB)
        df.loc[i, "ER Date Acquired (KRW)"] = exrate
        df.loc[i, "Adjusted Cost Basis (KRW)"] = row["Adjusted Cost Basis"] * exrate

        date = row["Date Sold"]
        exrate = get_exrate(date, USD_KRW_DB)
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


def get_exrate(date: str, USD_KRW_DB: dict) -> float:
    """Fetches the exchange rate for a given date."""

    if date in USD_KRW_DB:
        return USD_KRW_DB[date]
    else:
        raise AssertionError(f"Date {date} not found in USD_KRW_DB")


def print_gain_tax(total_gain_loss: float, total_gain_loss_krw: float) -> None:

    print("-" * 37)
    print("Total Gain/Loss:" + f"{total_gain_loss:,.2f} USD".rjust(20))
    print("Total Gain/Loss:" + f"{round(total_gain_loss_krw):,} KRW".rjust(20))
    print("-" * 37)


def parse_args():
    """Parses command-line arguments for file paths."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file-path",
        type=str,
        required=True,
        help="Path to the E*Trade 'G&L_Collapsed.xlsx' file",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=True,
        help="Path to the output CSV file, where 'etrade' should be included in the file name",
    )
    parser.add_argument(
        "--use-crawling",
        type=bool,
        default=False,
        help="Use web crawling to get transaction data (default: False)",
    )
    args = parser.parse_args()

    return args


if __name__ == "__main__":

    if DEBUG:
        # In debug mode, use a specific file and year
        year = 2024
        base_dir = f"{year}"
        file_path = f"{base_dir}/{year}_G&L_Collapsed.xlsx"
        output_path = f"{base_dir}/{year}_etrade.csv"
        use_crawling = True
        add_KRW_info(file_path, output_path, use_crawling)
    else:
        args = parse_args()
        add_KRW_info(args.file_path, args.output_path, args.use_crawling)
