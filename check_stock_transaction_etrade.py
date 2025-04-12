import datetime
import pandas as pd
from pathlib import Path
from common.headers import ETRADE_HEADER


def main():
    year = 2024
    base_dir = Path(f"{year}")
    df_raw = pd.read_excel(
        base_dir / f"{year}_G&L_Collapsed.xlsx", sheet_name="G&L_Collapsed"
    )

    # Remain columns to use
    df = df_raw.dropna(axis=0, how="any")
    df = df.reindex(columns=ETRADE_HEADER, fill_value=None)

    # Get all the dates (by hands)
    # from url = "http://www.smbs.biz/ExRate/TodayExRate.jsp"
    dates = list(set(df["Date Acquired"].tolist() + df["Date Sold"].tolist()))
    dates.sort()
    date_dict = {
        "01/31/2024": 1330.60,
        "02/20/2024": 1333.80,
        "02/21/2024": 1337.90,
        "03/07/2024": 1335.70,
        "05/20/2024": 1355.20,
        "05/21/2024": 1356.20,
        "08/20/2024": 1337.80,
        "08/21/2024": 1332.00,
    }
    for date in dates:
        if date in date_dict.keys():
            continue
        date_obj = datetime.datetime.strptime(date, "%m/%d/%Y")
        date_new = date_obj.strftime("%Y%m%d")
        print(date, date_new)

    # Update KRW-based columns
    def convert_date(date_col):
        date = row[date_col]
        if date in date_dict:
            return date_dict[date]
        else:
            raise AssertionError(f"Date {date} not found in date_dict")

    for i, row in df.iterrows():
        df.loc[i, "ER Date Acquired (KRW)"] = convert_date("Date Acquired")
        df.loc[i, "Adjusted Cost Basis (KRW)"] = row[
            "Adjusted Cost Basis"
        ] * convert_date("Date Acquired")

        df.loc[i, "ER Date Sold (KRW)"] = convert_date("Date Sold")
        df.loc[i, "Total Proceeds (KRW)"] = row["Total Proceeds"] * convert_date(
            "Date Sold"
        )
        gain_krw = (
            df.loc[i, "Total Proceeds (KRW)"] - df.loc[i, "Adjusted Cost Basis (KRW)"]
        )
        df.loc[i, "Adjusted Gain/Loss (KRW)"] = gain_krw

    # Total gain/loss
    total_gain_loss = df["Adjusted Gain/Loss"].sum()
    total_gain_loss_krw = df["Adjusted Gain/Loss (KRW)"].sum()
    print(f"Total Gain/Loss: ${total_gain_loss:.2f}")
    print(f"Total Gain/Loss (KRW): {total_gain_loss_krw:,}")

    # Save to csv
    df.to_csv(base_dir / f"{year}_etrade.csv", index=False)


if __name__ == "__main__":
    main()
