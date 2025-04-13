import re
import time
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class Crawler:
    def __init__(self, headless: bool = True) -> None:
        self.response = None
        self.driver = None
        self.page_state = ""
        self.options = Options()

        # Set basic options
        self.options.add_argument("--log-level=3")  # Suppress warnings and errors
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-blink-features=AutomationControlled")

        # For debugging
        self.options.add_experimental_option("detach", True)  # Prevent auto-shutdown

        # Set options selectively
        if headless:
            self.options.add_argument("--headless=new")
            self.options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        else:
            self.options.add_experimental_option("detach", True)
            self.options.add_argument("--remote-debugging-port=9222")

    def open_page(self, url: str) -> None:
        if self.driver is None:
            self.driver = webdriver.Chrome(options=self.options)

        # Open the target page
        self.driver.get(url=url)
        time.sleep(random.uniform(1, 2))

        # Close the pop-up window
        self.driver.execute_script("closeMainPopup();")

    def get_USD_KRW_rate(self, target_date: str) -> None:

        input_field = self.driver.find_element(By.ID, "searchDate")
        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('focus'));
            arguments[0].value = '';  // Delete the existing value
            arguments[0].value = arguments[1];  // Add the desired value
            arguments[0].dispatchEvent(new Event('blur'));                                   
        """,
            input_field,
            target_date,
        )

        # Page update after inputting the target date and close the pop-up window
        self.driver.execute_script("doSearch('frm_SearchDate');")
        time.sleep(random.uniform(1, 2))
        self.driver.execute_script("closeMainPopup();")

        # Extract the KRW exchange rate from the page
        info_txt = self.driver.find_element(By.CLASS_NAME, "table_type7").text
        match = re.search(r"미국 달러 \(USD\)\s+([\d,]+\.\d+)", info_txt)
        if match:
            result = match.group(1)
            return float(result.replace(",", ""))
        else:
            print("Can't find the value.")
            return None

    def deinit(self):
        if self.driver is not None:
            self.driver.quit()
