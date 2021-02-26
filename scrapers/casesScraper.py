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

    def get_driver(self):
        # get Chrome driver
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--headless")
        driver = webdriver.Chrome(executable_path=chrome_path, options=chromeOptions)
        return driver

    def render_page(self, url, driver):
        # render page using Chrome driver
        driver.get(url)
        time.sleep(3)
        r = driver.page_source
        # driver.quit()
        return r

    def scrape_cases(self):
        try:
            oyezDomain = "https://www.oyez.org/"
            oyezCasesUrl = "https://www.oyez.org/cases/"
            url = "".join([oyezCasesUrl, "2020/"])
            driver = self.get_driver()

            # get page
            r = self.render_page(url, driver)

            # get soup for page
            soup = BeautifulSoup(r, "html.parser")

            # get article
            article = soup.find("article")

            # get all cases
            cases = article.find_all("li")

            for case in cases:
                caseDict = dict.fromkeys(
                    [
                        "caseName",
                        "caseDocket",
                        "casePetitioner",
                        "caseRespondent",
                        "caseDecidedBy",
                        "caseLowerCourt",
                        "caseCitation",
                        "caseGranted",
                        "caseDescription",
                        "caseFacts",
                        "caseQuestion",
                        "caseArgued",
                    ],
                    None,
                )

                # get name
                caseDict["caseName"] = case.find("h2").get_text()

                # get link to case
                caseUrl = case.find("a")["href"]
                caseUrl = "".join([oyezDomain, caseUrl])
                print(caseUrl)

                try:
                    # get case page
                    casePage = self.render_page(caseUrl, driver)
                    caseSoup = BeautifulSoup(casePage, "html.parser")

                    caseArticle = caseSoup.find("article")

                    caseHeaders = caseArticle.find_all("h3")

                    # casePetitioner = None
                    # caseDocket = None
                    # caseRespondent = ""
                    # testa = None

                    for header in caseHeaders:
                        if header.get_text() == "Petitioner":
                            caseDict["casePetitioner"] = header.next_sibling.strip()

                    print(caseDict["casePetitioner"])
                    print(caseDict["testa"])

                    print(caseArticle.find_all("h3"))
                except Exception as e:
                    print(
                        "Failed to scrape case:{}\nError: {}".format(
                            caseDict["caseName"], e
                        )
                    )

        except Exception as e:
            print("Failed to scrape cases, error:{}".format(e))


if __name__ == "__main__":
    casesScraper = CasesScraper()
    casesScraper.scrape_cases()