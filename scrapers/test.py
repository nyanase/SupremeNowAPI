from urllib.parse import urlparse
# from urlparse import urlparse  # Python 2
url = "https://mondrian.mashable.com/2021%252F03%252F16%252Fde%252F17c7b97375614eff9a3101c524b8bdc7.3ddd9.jpg%252F1200x630.jpg?signature=hVkjCyubP0Ak6Mnye3LA3kpUeCE="
parsed_uri = urlparse(url)
result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
print(url.split(result)[1])