import requests
import urllib
import os
from newsapi import NewsApiClient
from newspaper import Article
import ast
from urllib.parse import urlparse
import json
import socket

class ArticlesScraper():
    def __init__(self, dev=True, timeout=15):
        self.server = "http://localhost:3000"
        if not dev:
            self.server = "https://supremenow-api.herokuapp.com"
        # self.news_api_client = NewsApiClient(api_key="f4a91eac4aa740af84a93939f587d11c")
        self.news_api_client = NewsApiClient(api_key="05e5224a10654221ac28569d92d518f2")
        socket.setdefaulttimeout(timeout)
        
    def get_top_articles(self, q, docket, content=False):
        articles = self.news_api_client.get_everything(q=q)["articles"]
        tot_articles_posted = 0
        for newsapi_article in articles: 
            article_dict = { 
                "source": "",
                "author": "",
                "title": "",
                "content": "",
                "description": "",
                "url": "",
                "image_url": "",
                "published": "", 
                "docket": ""  
            }
            
            article_dict["source"] = newsapi_article["source"]["name"]
            article_dict["author"] = newsapi_article["author"]
            article_dict["title"] = newsapi_article["title"]
            article_dict["description"] = newsapi_article["description"]
            article_dict["url"] = newsapi_article["url"]
            article_dict["image_url"] = newsapi_article["urlToImage"]
            article_dict["published"] = newsapi_article["publishedAt"]
            article_dict["docket"] = docket
            
            if content:
                article_dict["content"] = self.get_content(article_dict["url"])
            
            _id = ""
            
            try:    
                _id = self.post_article_content(article_dict)
                tot_articles_posted += 1
            except Exception as e:
                print("Could not post {}, error: {}".format(article_dict["url"], e))
            
            try:
                self.post_article_image(article_dict["image_url"], _id)
            except Exception as e:
                print("Could not post image {}, error: {}".format(article_dict["url"], e))
            
        return tot_articles_posted        
        
    def get_content(self, url):
        article_dict = Article(url)

        article_dict.download()
        article_dict.parse()
        
        return article_dict.text
    
    def scrape_articles(self): 
        # get names of all cases
        # for each name in cases
        return
        
    def post_article_content(self, article_dict):
        
        response = requests.post(
            "{}/articles/content".format(self.server),
            json={
                "source": article_dict["source"],
                "author": article_dict["author"],
                "title": article_dict["title"],
                "content": article_dict["content"],
                "description": article_dict["description"],
                "url": article_dict["url"],
                "image_url": article_dict["image_url"],
                "published": article_dict["published"],
                "docket": article_dict["docket"]
            },
        )
        # print(response.text)
        if response.ok:
            print("Article saved successfully, url: {}, docket: {}".format(article_dict["url"], article_dict["docket"]))
        else:
            raise Exception(response.status_code, response.text)            
        
        return json.loads(response.text)["_id"]

        
    
    def post_article_image(self, image_url, id):
        # image_format = image_url[image_url.rfind('.'):]
        # image_name = "".join([id, image_format])
        parsed_uri = urlparse(image_url)
        result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        image_name = image_url.split(result)[1].split("/")[-1]

        # adds headers to request so the image can be downloaded (or else its forbidden)
        opener = urllib.request.build_opener()
        opener.addheaders = [
            (
                "user-agent",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
            )
        ]
        urllib.request.install_opener(opener)

        # download image
        try:
            urllib.request.urlretrieve(image_url, os.path.basename(image_name))
        except:
            raise Exception("Timeout: Could not download image") 

        # open the image and add it as the image for the article
        with open(image_name, "rb") as image:

            # add image to article
            r = requests.post(
                "{}/articles/image/{}".format(self.server, id),
                files={"image": image},
            )
            if r.ok:
                print("Saved image successfully")
            else:
                os.remove(image_name)
                raise Exception(r.status_code, r.text)
            
            # close the image
            image.close()
        os.remove(image_name)
        
    def get_articles_for_case(self, case, content=False):
        
        docket = case["docket"]
        name = case["name"]
        petitioner = case["petitioner"] 
        respondent = case["respondent"]
        apellant = case["appellant"]
        appellee = case["appellee"]
        
        tot_articles_posted = 0
        
        tot_articles_posted += self.get_top_articles(name, docket)
        
        if tot_articles_posted < 5 and petitioner is not None:
            tot_articles_posted += self.get_top_articles(petitioner, docket)
        if tot_articles_posted < 5 and respondent is not None:
            tot_articles_posted += self.get_top_articles(respondent, docket)
        if tot_articles_posted < 5 and apellant is not None:
            tot_articles_posted += self.get_top_articles(apellant, docket)
        if tot_articles_posted < 5 and appellee is not None:
            tot_articles_posted += self.get_top_articles(appellee, docket)
            
    def get_all_cases(self, active=True):
        active = ""
        if active:
            active = "/active"
        
        url = self.server + "/cases{}".format(active)
        try: 
            cases = requests.get(url)
        except Exception as e:
            print("Could not get all cases, error: {}".format(e))
            
        return cases.json()

    
    def scrape_articles_all_cases(self, content=False, checkpoint=None):
        cases = self.get_all_cases()
        
        if checkpoint:
            idx = 0
            for i in range(len(cases)):
                if cases[i]["docket"] != checkpoint:
                    continue
                else:
                    idx = i
            while idx < len(cases):
                self.get_articles_for_case(cases[idx])
                idx += 1
                
        else:
            for case in cases:
                self.get_articles_for_case(case)
        
        print("All articles for all cases scraped")
        
        
    def scrape_all_articles(self, content=False, checkpoint=None):
        
        if checkpoint:
            self.scrape_articles_all_cases(checkpoint=checkpoint)
        else:
            self.get_top_articles("supreme court", "main", content)
            self.scrape_articles_all_cases(content)
            
        
        print("Got all articles for the day")    
        
        
if __name__ == "__main__":
    articles_scraper = ArticlesScraper(dev=False)
    
    # PREVIOUS CHECKPOINT = 19-438
    
    articles_scraper.scrape_all_articles(checkpoint="19-438")
    # cases = articles_scraper.get_all_cases()
    # articles_scraper.get_articles_for_case(cases[0])
    
    # articles_scraper.get_top_articles("hello", "test")
    
    # article_dict = { 
    #     "source": "a",
    #     "author": "b",
    #     "title": "c",
    #     "content": "d",
    #     "description": "e",
    #     "url": "f",
    #     "image_url": "g",
    #     "published": "h", 
    #     "docket": "i"  
    # }
    # _id = articles_scraper.post_article_content(article_dict)
    
    # print(_id)
    
    # articles_scraper.post_article_image("https://cdn.vox-cdn.com/thumbor/IdgNJaOIQBsN8QbQcH2MDU6sAUA=/0x243:2040x1311/fit-in/1200x630/cdn.vox-cdn.com/uploads/chorus_asset/file/10432811/mdoying_180308_2373_0091still.jpg", "605294c533f04e35e0eed118")