# Stock Transaction Analyzer for Oversease Securities Transfer Income Tax

## Overview

This Python script simplifies the process of preparing income tax data for overseas securities transactions in Korea, specifically targeting transactions handled by E*TRADE and Kiwoom. It automates several key tasks:

* **Data Processing:**  Handles transaction data for E*TRADE to add KRW-based columns and save as a CSV file.
* **Gain & Loss Calculation:**  Calculates capital gains and losses for each stock transaction.
* **Consolidated Reporting:**  Generates a comprehensive Excel report summarizing all transactions and calculated gains/losses and directly applicable to capital gains tax filing with the National Tax Service of Korea.

## Prerequisites

* **Python 3.10** 
* **pandas** library:  Install with `pip install pandas`

##  Data Preparation

1. **E*TRADE:**  

    -  Download your transaction history (G&L_Collapsed.xlsx) from the [E*TRADE website](https://us.etrade.com).

2. **Other Firms:**

    -  Follow each firm's specific instructions for exporting your transaction history as a CSV file.
    -  The name of the CSV file should include the firm name, e.g., "kiwoon" to be recognized.
    -  You need to implement the parsing class in `common/data_gen.py` to add the new firm's specific CSV information.

3. **Supported Firms:**

    -  Currently, the script supports E*TRADE (etrade) and Kiwoom (kiwoom).
    

3. **Exchange Rates:**

    -  You will need to manually add the relevant KRW exchange rate for each date present in the E*TRADE xlsx file within the `EXRATE_DICT` dictionary in `check_stock_transaction_etrade.py`.  An automatic solution for this is planned.

## Running the Scripts

1. **Generate CSV Files with KRW Information for E*TRADE:**

    ```bash
    python check_stock_transaction_etrade.py --file-path path/to/G&L_Collapsed.xlsx --output-path path/to/*etrade*.csv
    ```

    - Replace `path/to/G&L_Collapsed.xlsx` with the path to your downloaded E*TRADE Excel file.
    - Replace `path/to/*etrade*.csv` with the desired output path for the generated CSV files.

2. **Generate Final Gain & Loss Table:**

    ```bash
    python build_final_table.py --csv-dir path/to/csv --output-path path/to/*gain_final_save.xlsx --format-path path/to/output.xlsx
    ```

    - Replace `path/to/csv` with the directory containing all CSV files (E*TRADE, Kiwoom and others).
    - Replace `path/to/*gain_final_save.xlsx` with the desired output path for the consolidated gain/loss table. 
    - Replace `path/to/output.xlsx` with the path to a template XLSX file.

     - **Note:** 
       - The contents of the output XLSX file produced by `build_final_table.py` should be copied and pasted into your preferred final file format (e.g., an Excel workbook). 

##  Future Enhancements

* Automatic exchange rate retrieval.
* Save the final xlsx file is compatible with the given format from national tax service of Korea.
