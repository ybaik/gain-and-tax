import pandas as pd
from pathlib import Path
from common.data_gen import create_data_gen


TAX_RATE = 0.22
TAX_REDUCTION = 2500000


def print_gain_tax(total_gain_loss: int):
    tax_base = max(total_gain_loss - TAX_REDUCTION, 0)
    tax = round(tax_base * TAX_RATE)

    print(f"{'Total gain/loss:':<20} {total_gain_loss:,} KRW")
    print(f"{'Tax base:':<20} {tax_base:,} KRW (gain - basic deduction)")
    print(f"{'Tax payable:':<20}  {tax:,} KRW")


def main():
    year = 2024
    base_dir = Path(f"{year}")
    df_raw = pd.read_excel(base_dir / f"{year}_gain_final.xlsx", sheet_name="자료")

    input_list = [
        "2024_kiwoom_무매.csv",
        "2024_kiwoom_해외.csv",
        "2024_etrade.csv",
    ]

    print(input_list)
    for input in input_list:
        brokerage_firm = create_data_gen(base_dir / input)
        data = brokerage_firm.gen_data()
        df_raw = pd.concat([df_raw, pd.DataFrame(data)], ignore_index=True)

    # Check total gain/loss and tax
    total_gain_loss = (
        df_raw["양도가액"].sum() - df_raw["취득가액"].sum() - df_raw["필요경비"].sum()
    )
    print_gain_tax(total_gain_loss)

    df_raw.to_excel(base_dir / f"{year}_gain_final_save.xlsx", index=False)


if __name__ == "__main__":
    main()
