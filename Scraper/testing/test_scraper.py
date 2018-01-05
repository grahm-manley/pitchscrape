import sys
sys.path.append('..')
import Scraper
from bs4 import BeautifulSoup

file = open('html/scraper_test1.html')
page = file.read()
soup = BeautifulSoup(page, 'html.parser')
file.close()

'''
def test_get_review_urls():
	for review_url in Scraper:
		print(review_url)
'''
def test_get_unsaved_reviews():
	for review in Scraper.get_unsaved_reviews():
		print(review.album_title)

