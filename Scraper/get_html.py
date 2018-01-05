import requests

url = 'https://pitchfork.com/reviews/albums/?page=1'
headers = {'User-Agent':'Mozilla/5.0'}
response = requests.get(url, headers=headers)
page = response.content
print(page)
