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

# driver = webdriver.Chrome(executable_path=chrome_path)

# driver.get('https://techwithtim.net')

# from webdriver_manager.chrome import ChromeDriverManager


class CasesScraper:
    def __init__(self, dev=True):
        self.server = "http://localhost:3000"
        if not dev:
            self.server = (
                "http://ec2-18-191-246-32.us-east-2.compute.amazonaws.com:3000"
            )
        self.driver_path = r"/usr/local/bin/chromedriver"
        self.oyez_domain = "https://www.oyez.org/"

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
                    ],
                    None,
                )

                # get name
                case_dict["name"] = case.find("h2").get_text()

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
                    except:
                        print("Couldn't post")
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

    def post_cases(self, case_dict):

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
            },
        )
        print(response.text)

        if not response.ok:
            raise Exception("Failed to post")

    def scrape_all_cases(self):
        # get all scrapable years
        year_urls = self.get_scrapable_years()

        complete_err_list = []

        # scrape all cases for each year
        for year_url in year_urls:
            err_list = self.scrape_cases_by_year(year_url)
            complete_err_list.append(err_list)

        print("COMPLETE ERROR LIST: {}".format(complete_err_list))


if __name__ == "__main__":
    casesScraper = CasesScraper(dev=False)
    casesScraper.scrape_all_cases()
    # casesScraper.scrape_single_case("https://www.oyez.org/cases/2018/18-726")
    # casesScraper.scrape_cases_by_year("cases/2020")

# def scrape_single_case(self, case_url):
#     try:
#         # get case page
#         case_dict = dict.fromkeys(
#             [
#                 "docket",
#                 "petitioner",
#                 "respondent",
#                 "appellant",
#                 "appellee",
#                 "decidedBy",
#                 "lowerCourt",
#                 "citation",
#                 "granted",
#                 "facts",
#                 "question",
#                 "argued",
#                 "decided",
#             ],
#             None,
#         )

#         driver = self.get_driver()
#         case_page = self.render_page(case_url, driver)
#         case_soup = BeautifulSoup(case_page, "html.parser")

#         case_article = case_soup.find("article")

#         case_headers = case_article.find_all("h3")

#         # get each case attribute

#         for header in case_headers:
#             if header.get_text() == "Petitioner":
#                 case_dict["petitioner"] = header.next_sibling.strip()
#             if header.get_text() == "Respondent":
#                 case_dict["respondent"] = header.next_sibling.strip()
#             if header.get_text() == "Docket no.":
#                 case_dict["docket"] = header.next_sibling.strip()
#             if header.get_text() == "Decided by":
#                 case_dict["decidedBy"] = header.find_next_sibling().get_text()
#             if header.get_text() == "Lower court":
#                 case_dict["lowerCourt"] = header.next_sibling.strip()
#             if header.get_text() == "Citation":
#                 case_dict["citation"] = header.find_next_sibling().get_text()
#                 try:
#                     case_dict["citation"] = datetime.strptime(
#                         case_dict["citation"].replace(",", ""),
#                         "%b %d %Y",
#                     ).strftime("%Y-%m-%d")
#                 except:
#                     pass
#             if header.get_text() == "Granted":
#                 case_dict["granted"] = header.find_next_sibling().get_text()
#                 try:
#                     case_dict["granted"] = datetime.strptime(
#                         case_dict["granted"].replace(",", ""),
#                         "%b %d %Y",
#                     ).strftime("%Y-%m-%d")
#                 except:
#                     pass
#             if header.get_text() == "Argued":
#                 case_dict["argued"] = header.find_next_sibling().get_text()
#                 try:
#                     case_dict["argued"] = datetime.strptime(
#                         case_dict["argued"].replace(",", ""), "%b %d %Y"
#                     ).strftime("%Y-%m-%d")
#                 except:
#                     pass
#             if header.get_text() == "Decided":
#                 case_dict["decided"] = header.find_next_sibling().get_text()
#                 try:
#                     case_dict["decided"] = datetime.strptime(
#                         case_dict["decided"].replace(",", ""), "%b %d %Y"
#                     ).strftime("%Y-%m-%d")
#                 except:
#                     pass

#         case_sections = case_article.find_all("section")

#         # get case fact

#         case_facts_paragraphs = case_sections[0].find_all("p")
#         case_facts = ""
#         for paragraph in case_facts_paragraphs:
#             case_facts = "".join([case_facts, paragraph.get_text(), "\n"])
#         case_dict["facts"] = case_facts

#         # get case question

#         # single question
#         try:
#             case_dict["question"] = case_sections[1].find("p").get_text()
#         except:
#             pass

#         # list questions
#         try:
#             questions = case_sections[1].find_all("li")
#             question = ""
#             for i in range(len(questions)):
#                 question = "".join(
#                     [question, "{}. {}\n".format((i + 1), questions[i].get_text())]
#                 )
#             case_dict["question"] = question
#         except:
#             pass

#         print(case_dict)

#     except Exception as e:
#         print("Failed to scrape case, Error: {}".format(e))
#         # exc_type, exc_obj, exc_tb = sys.exc_info()
#         # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         # print(exc_type, fname, exc_tb.tb_lineno)
