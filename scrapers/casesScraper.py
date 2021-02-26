import requests
import re
import os
import urllib
import json
from bs4 import BeautifulSoup
from lxml import html
import time
from selenium import webdriver

chrome_path = r"/usr/local/bin/chromedriver"

# driver = webdriver.Chrome(executable_path=chrome_path)

# driver.get("https://techwithtim.net")

# from webdriver_manager.chrome import ChromeDriverManager


class CasesScraper:
    def __init__(self, dev=True):
        self.server = "http://localhost:3000"
        if not dev:
            self.server = (
                "http://ec2-18-191-246-32.us-east-2.compute.amazonaws.com:3000"
            )
        self.driverPath = r"/usr/local/bin/chromedriver"

    def render_page(self, url):
        # render page using Chrome driver
        driver = webdriver.Chrome(executable_path=chrome_path)
        driver.get(url)
        time.sleep(3)
        r = driver.page_source
        # driver.quit()
        return r

    def scrape_cases(self):
        try:
            url = "https://www.oyez.org/cases/2020"
            r = self.render_page(url)

            # get soup for page
            soup = BeautifulSoup(r, "html.parser")

            # get article
            article = soup.find("article")

            # get all cases
            cases = article.find_all("li")

            for case in cases:
                title = case.find("h2").get_text
                print(title.get_text())
        except Exception as e:
            print(e)
            print("hola")


if __name__ == "__main__":
    casesScraper = CasesScraper()
    casesScraper.scrape_cases()