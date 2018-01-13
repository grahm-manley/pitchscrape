import sys
sys.path.append('..')
import scraper 
from unittest.mock import patch
from datetime import datetime
class response_mock:
	def __init__(self, html):
		self.content = html

def req_mock(url, headers):
	base_url = 'https://pitchfork.com/reviews/albums/'	
	html_dir = 'html/scraper/'
	
	file_path = url.replace(base_url, html_dir)
	if(file_path[-1:] == '/'):
		file_path = file_path[:-1] + '.html'
	else:
		file_path += '.html'
	
	file = open(file_path)
	html = file.read()
	file.close()
	return response_mock(html)

@patch('requests.get', new = req_mock)
def test_get_unsaved_reviews():
	scrape = scraper.Scraper(datetime(2018, 1, 3))
	file = open('correct/scraper1.txt')
	correct_results = file.read()
	file.close()
	test_results = ''
	for review in scrape.get_unsaved_reviews():
		test_results += (str(review.artists) + '\n')
		test_results += (review.album_title + '\n')
		test_results += (review.score + '\n')
	assert(test_results == correct_results)

