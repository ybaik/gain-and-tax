import pandas as pd
from pathlib import Path
from datetime import datetime


def create_data_gen(file_path: Path) -> None:
    if "kiwoom" in file_path.stem:
        return DataGenKiwoom(file_path)
    elif "etrade" in file_path.stem:
        return DataGenETrade(file_path)
    elif "miraeasset" in file_path.stem:
        return DataGenMiraeAsset(file_path)
    else:
        print(f"Unknown firm type: {file_path.stem}")
        return None


def convert_to_amount(amount: str | int) -> int:
    if isinstance(amount, str):
        return int(amount.replace(",", "").strip())
    elif isinstance(amount, int):
        return amount
    elif isinstance(amount, float):
        return int(amount)
    else:
        raise ValueError("Invalid amount type")


class DataGen:
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def _get_basic_info(self):
        info_basic = {
            "주식 종목명": None,
            "국내/국외 구분": "2",
            "취득유형별\n양도주식 수": None,  # int
            "세율구분": "61",
            "주식등 종류": "61",
            "양도물건 종류": "10",
            "취득유형": "01",
            "양도일자": None,  # 날짜 2023-06-19
            "양도가액": None,  # int
            "취득일자": None,  # 날짜 2023-06-19
            "취득가액": None,  # int
            "필요경비": None,  # int
            "국제증권식별번호\n(ISIN코드)": None,  # str
            "국외자산국가코드": "US",
            "국외자산내용": "증권",
        }
        return info_basic


class DataGenETrade(DataGen):
    def __init__(self, filepath: Path) -> None:
        super().__init__(filepath)
        self.df = pd.read_csv(filepath)

    def gen_data(self):

        output_list = []
        for _, row in self.df.iterrows():
            info_basic = self._get_basic_info()
            info_basic["주식 종목명"] = "퀄컴"
            info_basic["취득유형별\n양도주식 수"] = convert_to_amount(row["Qty."])
            info_basic["양도일자"] = datetime.strptime(
                row["Date Sold"], "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
            info_basic["양도가액"] = convert_to_amount(row["Total Proceeds (KRW)"])
            info_basic["취득일자"] = datetime.strptime(
                row["Date Acquired"], "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
            info_basic["취득가액"] = convert_to_amount(row["Adjusted Cost Basis (KRW)"])
            info_basic["필요경비"] = 0
            info_basic["국제증권식별번호\n(ISIN코드)"] = "US7475251036"
            output_list.append(info_basic)

        return output_list


class DataGenKiwoom(DataGen):
    def __init__(self, filepath: Path) -> None:
        super().__init__(filepath)

        df = pd.read_csv(filepath, encoding="euc-kr")
        if "종목코드" not in df.keys():
            df = pd.read_csv(filepath, encoding="euc-kr", skiprows=1)
        self.df = df

    def gen_data(self):

        output_list = []
        for _, row in self.df.iterrows():
            info_basic = self._get_basic_info()
            info_basic["주식 종목명"] = row["종목명"]
            info_basic["취득유형별\n양도주식 수"] = convert_to_amount(row["매도수량"])
            info_basic["양도일자"] = row["매도일"].replace("/", "-")
            info_basic["양도가액"] = convert_to_amount(row["매도금액"])
            info_basic["취득일자"] = row["매수일"].replace("/", "-")
            info_basic["취득가액"] = convert_to_amount(row["매수금액"])
            info_basic["필요경비"] = convert_to_amount(row["필요경비"])
            info_basic["국제증권식별번호\n(ISIN코드)"] = row["종목코드"]
            output_list.append(info_basic)

        return output_list


class DataGenMiraeAsset(DataGen):
    def __init__(self, filepath: Path) -> None:
        super().__init__(filepath)
        df = pd.read_csv(filepath, encoding="euc-kr")
        self.df = df.dropna(axis=0, how="any")

    def gen_data(self):

        output_list = []
        for _, row in self.df.iterrows():
            info_basic = self._get_basic_info()
            info_basic["주식 종목명"] = row["종목명"]
            info_basic["취득유형별\n양도주식 수"] = convert_to_amount(row["양도주식수"])
            info_basic["양도일자"] = row["양도일자"]
            info_basic["양도가액"] = convert_to_amount(row["양도가액(원)"])
            info_basic["취득일자"] = row["취득일자"]
            info_basic["취득가액"] = convert_to_amount(row["취득가액(원)"])
            info_basic["필요경비"] = convert_to_amount(row["필요경비(원)"])
            info_basic["국제증권식별번호\n(ISIN코드)"] = row["표준종목번호"]
            output_list.append(info_basic)

        return output_list
