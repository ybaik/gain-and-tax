import time
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class Crawler:
    def __init__(
        self,
        headless: bool = True,
        profile_path: str = "C:/Users/hyunx/AppData/Local/Google/Chrome/User Data",
    ) -> None:
        headless
        self.response = None
        self.driver = None
        self.page_state = ""
        self.options = Options()

        # Set basic options
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-blink-features=AutomationControlled")

        # For debugging
        self.options.add_experimental_option("detach", True)  # Prevent auto-shutdown

        # Set options selectively
        if headless:
            self.options.add_argument("--headless=new")
            self.options.add_argument("--ignore-certificate-errors")
            self.options.add_argument("--ignore-ssl-errors")

        else:
            self.options.add_argument(f"user-data-dir={profile_path}")
            self.options.add_argument("--remote-debugging-port=9222")
            self.options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )
            self.options.add_experimental_option("useAutomationExtension", False)

    def open_page(self, url: str) -> None:
        if self.driver is None:
            self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(url=url)
        self.page_state = self.driver.execute_script("return document.readyState")
        time.sleep(random.uniform(1, 2))
        return self.page_state

    def get(self, date: str) -> None:
        # input_field = self.driver.find_element(By.ID, "searchDate")
        # input_field.clear()
        # input_field.send_keys(date)
        # input_field.send_keys(Keys.RETURN)

        element = self.driver.find_elements(By.CLASS_NAME, "table_type7")

        # content > div:nth-child(9) > table

        time.sleep(3)
        return element.text

    def deinit(self):
        if self.driver is not None:
            self.driver.quit()
