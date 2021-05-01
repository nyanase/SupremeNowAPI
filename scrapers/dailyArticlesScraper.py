from articlesScraper import ArticlesScraper

articles_scraper = ArticlesScraper(dev=False)
# print(len(articles_scraper.get_all_cases()))

articles_scraper.scrape_all_articles()



