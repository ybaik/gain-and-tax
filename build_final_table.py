import argparse
import pandas as pd
from pathlib import Path
from common.data_gen import create_data_gen


DEBUG = False

TAX_RATE = 0.22
TAX_REDUCTION = 2500000


def print_gain_tax(total_gain_loss: int) -> None:
    tax_base = max(total_gain_loss - TAX_REDUCTION, 0)
    tax = round(tax_base * TAX_RATE)

    print("-"*38)
    print("Total Gain/Loss\t:" + f"{total_gain_loss:,} KRW".rjust(20))
    print("Tax Base\t:" + f"{tax_base:,} KRW".rjust(20))
    print("Tax Payable\t:" + f"{tax:,} KRW".rjust(20))
    print("-"*38)


def extract_tax_info(csv_dir: Path, output_path: Path, format_path: Path) -> None:
    """Extracts tax information from the given CSV files in csv_dir and adds it to the given Excel file.
    Args:
        csv_dir (Path): Path to the directory containing the CSV files that will be read.
        output_path (Path): Path to the Excel file where the tax information will be added.
        format_path (Path): Path to the Excel file containing the format.
    """
    # Read Excel file
    df_raw = pd.read_excel(format_path, sheet_name="자료")

    # Read CSV files
    for input_csv_path in csv_dir.glob("*.csv"):
        brokerage_firm = create_data_gen(input_csv_path)
        data = brokerage_firm.gen_data()
        df_raw = pd.concat([df_raw, pd.DataFrame(data)], ignore_index=True)

    # Check total gain/loss and tax
    total_gain_loss = (
        df_raw["양도가액"].sum() - df_raw["취득가액"].sum() - df_raw["필요경비"].sum()
    )
    print_gain_tax(total_gain_loss)

    # Save to Excel
    df_raw.to_excel(output_path, index=False)


def parse_args():
    """Parses command-line arguments for file paths."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv-dir", type=str, required=True)
    parser.add_argument("--output-path", type=str, required=True)
    parser.add_argument(
        "--format-path", type=str, default="format/2024_gain_final.xlsx"
    )
    args = parser.parse_args()

    return args


if __name__ == "__main__":

    if DEBUG:
        # In debug mode, use a specific file and year
        year = 2024
        base_dir = Path(f"{year}")
        csv_dir = base_dir
        output_path = base_dir / f"{year}_gain_final_save.xlsx"
        format_path = Path("format/2024_gain_final.xlsx")
        extract_tax_info(csv_dir, output_path, format_path)
    else:
        args = parse_args()
        extract_tax_info(args.csv_dir, args.output_path, args.format_path)
