from itertools import count
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from Review import Review

headers = {'User-Agent':'Mozilla/5.0'}
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
base_url = 'https://pitchfork.com' 
# LAST_RAN date is a placeholder until it is setup to pull the date from the DB
LAST_RAN = datetime.today() - timedelta(days=5)

def get_unsaved_reviews():
	for group_page in _get_review_group_pages():
		for review_url in _get_review_urls(group_page):
			response = requests.get(review_url, headers=headers)
			review_html = response.content
			soup = BeautifulSoup(review_html, 'html.parser')
			multiple_albums = soup.find(
				'div', 
				{'class':'multi-tombstone-widget'})	
			if(multiple_albums == None):
				yield Review(review_html)
			else:
				review_tags = soup.find_all(
					'div', 
					{'class':'single-album-tombstone'})
				for review in review_tags:
					yield Review(str(review))
			

def _get_review_group_pages():
	review_url_base = base_url + '/reviews/albums/?page='	
	for page_number in count(start=1):
		reviews_url = review_url_base + str(page_number)
		response = requests.get(reviews_url, headers=headers)
		page = BeautifulSoup(response.content, 'html.parser')
		#page = _get_url_soup(reviews_url)
		
		# Find most recent review on page
		time_tag = page.find('time')
		datetime_str = time_tag['datetime']
		datetime_obj = datetime.strptime(datetime_str, DATE_FORMAT)
		#most_recent_review_dttm = _get_most_recent_review_on_page(page)
		if(LAST_RAN < datetime_obj):
			yield page 
		else:
			raise StopIteration	

def _get_review_urls(page):
	reviews = page.find_all("div", {"class": "review"})
	for review in reviews :
		review_dttm_str = review.time['datetime']
		review_dttm_obj = datetime.strptime(review_dttm_str,DATE_FORMAT) 
		if(review_dttm_obj > LAST_RAN) :
			url_tag = review.find(('a', {'class':'album-link'}))
			url = base_url + url_tag['href']
			yield url		
		else:
			raise StopIteration	

'''
def _get_most_recent_review_on_page(page):
	time_tag = page.find('time')	
	datetime_str = time_tag['datetime']
	datetime_obj = datetime.strptime(datetime_str, DATE_FORMAT)
	return datetime_obj
def _get_url_soup(url):
	response = requests.get(url, headers=headers)
	soup = BeautifulSoup(response.content, 'html.parser')
	return soup 
'''
