from itertools import count
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from Review import Review

headers = {'User-Agent':'Mozilla/5.0'}
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
BASE_URL = 'https://pitchfork.com' 
# LAST_RAN date is a placeholder until it is setup to pull the date from the DB
LAST_RAN = datetime.today() - timedelta(days=5)

def get_unsaved_reviews():
	"""
	Retrieve the reviews that have been added to pitchfork since the 
	program was last ran. The function is a generator to allow for 
	separation between the class dealing with the database and the 
	scraper. This allows us to save each review to the db as it is 
	found without keeping it in memory.

	"""
	for group_page in _get_review_group_pages():
		for review_url in _get_review_urls(group_page):
			response = requests.get(review_url, headers=headers)
			review_html = response.content
			soup = BeautifulSoup(review_html, 'html.parser')

			# Find div for multiple albums if it exists 
			multiple_albums = soup.find(
				'div', 
				{'class':'multi-tombstone-widget'})	
			if(multiple_albums == None): # If one album on review
				yield Review(review_html)
			else: 
				# Get individual albums
				review_tags = soup.find_all(
					'div', 
					{'class':'single-album-tombstone'})
				# Make review object from individual album tags
				for review in review_tags:
					yield Review(str(review))
			

def _get_review_group_pages():
	""" 
	This function goes through the pages starting at 
	https://pitchfork.com/reviews/albums/?page=1 and iteratively returns
	the soup object of pages that contain unprocessed reviews. 
	"""
	review_url_base = BASE_URL + '/reviews/albums/?page='	

	for page_number in count(start=1): 	# Loop 1 -> inf
		reviews_url = review_url_base + str(page_number)
		response = requests.get(reviews_url, headers=headers)
		page = BeautifulSoup(response.content, 'html.parser')
		
		# Find most recent review on page
		time_tag = page.find('time')
		datetime_str = time_tag['datetime']
		datetime_obj = datetime.strptime(datetime_str, DATE_FORMAT)
		if(LAST_RAN < datetime_obj):
			yield page 
		else:
			raise StopIteration	

def _get_review_urls(page):
	"""
	Given a soup object of a page containing a list of reviews, 
	for example the html on: https://pitchfork.com/reviews/albums/?page=1,
	iteratively return the url of the reviews on that page that have been
	posted since the last time the script was run.
	"""

	reviews = page.find_all("div", {"class": "review"})
	for review in reviews :
		review_dttm_str = review.time['datetime']
		review_dttm_obj = datetime.strptime(review_dttm_str,DATE_FORMAT) 
		if(review_dttm_obj > LAST_RAN) :
			url_tag = review.find(('a', {'class':'album-link'}))
			url = BASE_URL + url_tag['href']
			yield url		
		else:
			raise StopIteration	

