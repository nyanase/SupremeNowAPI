# from newsapi import NewsApiClient

# api = NewsApiClient(api_key="f4a91eac4aa740af84a93939f587d11c")

# print(api.get_everything(q="American Medical Association v. Cochran")["articles"])

from newspaper import Article

url = "https://news.google.com/articles/CAIiEMjJsT6CdAl4tHYqUSN6DU8qFwgEKg8IACoHCAowhO7OATDh9Cgwv7tQ?hl=en-US&gl=US&ceid=US%3Aen"

article = Article(url)

article.download()
article.parse()

print(article.text)

# the name of the image when downloaded and the link to access it
# import urllib
# import requests
# import os

# image_name = f"hello.jpg"
# image_link = f"https://www.abajournal.com/images/main_images/abortiongavel2.jpg"

# # adds headers to request so the image can be downloaded (or else its forbidden)
# opener = urllib.request.build_opener()
# opener.addheaders = [
#     (
#         "user-agent",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
#     )
# ]
# urllib.request.install_opener(opener)

# # download image
# urllib.request.urlretrieve(image_link, os.path.basename(image_name))

# # open the image and add it as the image for the article
# with open(image_name, "rb") as image:

#     # add image to article
#     r = requests.post(
#         f"http://localhost:3000/articles/image/60528615c4ed482e8a80874c",
#         files={"image": image},
#     )
#     if r.ok:
#         print("Saved image successfully")
#     else:
#         print(r.text, r.status_code)
#         print("Sending image to server failed")

#     # close the image
#     image.close()
# os.remove(image_name)