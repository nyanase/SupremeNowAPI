import requests
import re
import os
import urllib
import json
from bs4 import BeautifulSoup
from lxml import html
import time
from selenium import webdriver
from datetime import datetime
import sys, os

chrome_path = r"/usr/local/bin/chromedriver"


class CasesScraper:
    def __init__(self, dev=True):
        self.server = "http://localhost:3000"
        if not dev:
            self.server = "https://supremenow-api.herokuapp.com"
        self.driver_path = r"/usr/local/bin/chromedriver"
        self.oyez_domain = "https://www.oyez.org/"
        self.year_urls = [
            'cases/2021','cases/2020','cases/2019', 'cases/2018', 'cases/2017', 'cases/2016', 'cases/2015', 'cases/2014', 
            'cases/2013', 'cases/2012', 'cases/2011', 'cases/2010', 'cases/2009', 'cases/2008', 'cases/2007', 'cases/2006', 
            'cases/2005', 'cases/2004', 'cases/2003', 'cases/2002', 'cases/2001', 'cases/2000', 'cases/1999', 'cases/1998', 
            'cases/1997', 'cases/1996', 'cases/1995', 'cases/1994', 'cases/1993', 'cases/1992', 'cases/1991', 'cases/1990', 
            'cases/1989', 'cases/1988', 'cases/1987', 'cases/1986', 'cases/1985', 'cases/1984', 'cases/1983', 'cases/1982', 
            'cases/1981', 'cases/1980', 'cases/1979', 'cases/1978', 'cases/1977', 'cases/1976', 'cases/1975', 'cases/1974', 
            'cases/1973', 'cases/1972', 'cases/1971', 'cases/1970', 'cases/1969', 'cases/1968', 'cases/1967', 'cases/1966', 
            'cases/1965', 'cases/1964', 'cases/1963', 'cases/1962', 'cases/1961', 'cases/1960', 'cases/1959', 'cases/1958', 
            'cases/1957', 'cases/1956', 'cases/1955', 'cases/1940-1955', 'cases/1900-1940', 'cases/1850-1900', 'cases/1789-1850'
        ]

    def get_driver(self):
        # get Chrome driver
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--headless")
        driver = webdriver.Chrome(
            executable_path=self.driver_path, options=chromeOptions
        )
        return driver

    def render_page(self, url, driver):
        # render page using Chrome driver
        driver.get(url)
        time.sleep(3)
        r = driver.page_source
        # driver.quit()
        return r

    def scrape_cases_by_year(self, year_url):
        try:
            url = "".join([self.oyez_domain, year_url])
            driver = self.get_driver()

            # get page
            r = self.render_page(url, driver)

            # get soup for page
            soup = BeautifulSoup(r, "html.parser")

            # get article
            article = soup.find("article")

            # get all cases
            cases = article.find_all("li")

            failed_cases = []

            for case in cases:
                case_dict = dict.fromkeys(
                    [
                        "name",
                        "docket",
                        "petitioner",
                        "respondent",
                        "appellant",
                        "appellee",
                        "decidedBy",
                        "lowerCourt",
                        "citation",
                        "granted",
                        "description",
                        "facts",
                        "question",
                        "argued",
                        "decided",
                        "year",
                    ],
                    None,
                )

                # get name
                case_dict["name"] = case.find("h2").get_text()

                # get year
                case_dict["year"] = year_url[-4:]

                # get description
                case_dict["description"] = case.find(
                    "div", {"class": "description"}
                ).get_text()

                # get link to case
                case_url = case.find("a")["href"]
                case_url = "".join([self.oyez_domain, case_url])
                print(case_url)

                try:
                    # get case page
                    case_page = self.render_page(case_url, driver)
                    case_soup = BeautifulSoup(case_page, "html.parser")

                    case_article = case_soup.find("article")

                    case_headers = case_article.find_all("h3")

                    # get each case attribute

                    for header in case_headers:
                        if header.get_text() == "Petitioner":
                            case_dict["petitioner"] = header.next_sibling.strip()
                        if header.get_text() == "Respondent":
                            case_dict["respondent"] = header.next_sibling.strip()
                        if header.get_text() == "Appellant":
                            case_dict["appellant"] = header.next_sibling.strip()
                        if header.get_text() == "Appellee":
                            case_dict["appellee"] = header.next_sibling.strip()
                        if header.get_text() == "Docket no.":
                            case_dict["docket"] = header.next_sibling.strip()
                        if header.get_text() == "Decided by":
                            case_dict[
                                "decidedBy"
                            ] = header.find_next_sibling().get_text()
                        if header.get_text() == "Lower court":
                            case_dict["lowerCourt"] = header.next_sibling.strip()
                        if header.get_text() == "Citation":
                            case_dict[
                                "citation"
                            ] = header.find_next_sibling().get_text()
                            try:
                                case_dict["citation"] = datetime.strptime(
                                    case_dict["citation"].replace(",", ""),
                                    "%b %d %Y",
                                ).strftime("%Y-%m-%d")
                            except:
                                pass
                        if header.get_text() == "Granted":
                            case_dict["granted"] = header.find_next_sibling().get_text()
                            try:
                                case_dict["granted"] = datetime.strptime(
                                    case_dict["granted"].replace(",", ""),
                                    "%b %d %Y",
                                ).strftime("%Y-%m-%d")
                            except Exception as e:
                                print(e)
                        if header.get_text() == "Argued":
                            case_dict["argued"] = header.find_next_sibling().get_text()
                            try:
                                case_dict["argued"] = datetime.strptime(
                                    case_dict["argued"].replace(",", ""), "%b %d %Y"
                                ).strftime("%Y-%m-%d")
                            except:
                                pass
                        if header.get_text() == "Decided":
                            case_dict["decided"] = header.find_next_sibling().get_text()
                            try:
                                case_dict["decided"] = datetime.strptime(
                                    case_dict["decided"].replace(",", ""), "%b %d %Y"
                                ).strftime("%Y-%m-%d")
                            except:
                                pass

                    case_sections = case_article.find_all("section")

                    # get case fact

                    case_facts_paragraphs = case_sections[0].find_all("p")
                    case_facts = ""
                    for paragraph in case_facts_paragraphs:
                        case_facts = "".join([case_facts, paragraph.get_text(), "\n"])
                    case_dict["facts"] = case_facts

                    # get case question

                    # single question
                    try:
                        case_dict["question"] = case_sections[1].find("p").get_text()
                    except:
                        # list question
                        try:
                            questions = case_sections[1].find_all("li")
                            question = ""
                            for i in range(len(questions)):
                                question = "".join(
                                    [
                                        question,
                                        "{}. {}\n".format(
                                            (i + 1), questions[i].get_text()
                                        ),
                                    ]
                                )
                            case_dict["question"] = question
                        except:
                            pass

                    print(case_dict)
                    try:
                        self.post_cases(case_dict)
                    except Exception as e:
                        print("Couldn't post", e)
                        failed_cases.append(case)

                except Exception as e:
                    failed_cases.append(case)
                    print(
                        "Failed to scrape case:{}\nError: {}".format(
                            case_dict["name"], e
                        )
                    )

            print("FAILED TO SCRAPE FOLLOWING CASES:\n{}".format(failed_cases))

            return failed_cases
        except Exception as e:
            print("Failed to scrape cases, error:{}".format(e))

    def get_scrapable_years(self):
        url = "".join([self.oyez_domain, "/cases"])
        driver = self.get_driver()

        # get page
        r = self.render_page(url, driver)

        # get soup for page
        soup = BeautifulSoup(r, "html.parser")

        # get each dropdown link
        terms_dropdowns = soup.find_all("div", {"class": "oy-index-control ng-scope"})[
            1
        ].find_all("li")

        year_urls = []

        for term in terms_dropdowns:
            year_urls.append(term.find("a")["href"])

        return year_urls
    
    def delete_case(self, docket):
        response = requests.delete(
            "{}/cases/docket/{}".format(self.server, docket)
        )
        
        if not response.ok:
            raise Exception("Failed to Delete")

    def post_cases(self, case_dict):
        try:
            self.delete_case(case_dict["docket"])
        except Exception as e:
            raise Exception(e)

        response = requests.post(
            "{}/cases".format(self.server),
            json={
                "name": case_dict["name"],
                "docket": case_dict["docket"],
                "petitioner": case_dict["petitioner"],
                "respondent": case_dict["respondent"],
                "decided_by": case_dict["decidedBy"],
                "lower_court": case_dict["lowerCourt"],
                "citation": case_dict["citation"],
                "granted": case_dict["granted"],
                "argued": case_dict["argued"],
                "decided": case_dict["decided"],
                "description": case_dict["description"],
                "facts": case_dict["facts"],
                "question": case_dict["question"],
                "year": case_dict["year"],
            },
        )
        print(response.text)

        if not response.ok:
            raise Exception("Failed to post")

    def scrape_all_cases(self):
        # get all scrapable years
        # year_urls = self.get_scrapable_years()
        # print(year_urls)

        complete_err_list = []

        # scrape all cases for each year
        for year_url in self.year_urls:
            err_list = self.scrape_cases_by_year(year_url)
            complete_err_list.append(err_list)

        print("COMPLETE ERROR LIST: {}".format(complete_err_list))


if __name__ == "__main__":
    casesScraper = CasesScraper(dev=True)
    casesScraper.scrape_all_cases()
    # casesScraper.scrape_single_case("https://www.oyez.org/cases/2018/18-726")
    # casesScraper.scrape_cases_by_year("cases/2020")