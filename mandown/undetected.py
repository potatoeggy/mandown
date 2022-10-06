import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By


class UndetectedDriver:
    def __init__(self) -> None:
        self.driver = uc.Chrome()
        self.first_time = True

    def get(self, url: str) -> str:
        self.driver.get(url)
        if self.first_time:
            time.sleep(5)
            self.first_time = False

        return self.driver.find_element(By.TAG_NAME, "html").get_attribute("outerHTML")
