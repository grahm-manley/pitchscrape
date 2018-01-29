import sys
import logging
import logging.config
from itertools import count
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
from core.review import Review
from core.db_connection import DbConnection
from core import config

headers = {'User-Agent':'Mozilla/5.0'}
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
BASE_URL = 'https://pitchfork.com' 

# Set up logger
logging.config.dictConfig(config.logging_config)
logger = logging.getLogger()
def scraper():
	logger.info("SCRAPE STARTED @ {}".format(datetime.now()))
	fails = []
	page_number = 1
	with DbConnection() as db:
		last_ran = db.get_last_update_time()
		saved_reviews = 0
		for review in get_unsaved_reviews(last_ran, start_page = page_number):
			logger.info('Scraped: ' +  review.album_title + 
				' by ' + str(review.artists))
			try:
				if(db.save_review(review)):
					saved_reviews = saved_reviews + 1
			except Exception as e:
				logger.error('Failed to save : ' + 
					review.album_title)
				logger.error(e)
				fails.append((review.album_title,
					review.artists))
				
			time.sleep(1) # For lessening the load on pitchfork

		db.update_last_run_date()

	logger.info("SCRAPE COMPLETED @ {}: Saved {} reviews with {} errors".format(
		datetime.now(), saved_reviews, len(fails))) 

	if(len(fails) > 0):
		logger.info("Fails: " + str(fails))


def get_unsaved_reviews(last_ran, start_page=1):
	"""
	Retrieve the reviews that have been added to pitchfork since 
	the program was last ran. The function is a generator to allow 
	for separation between the class dealing with the database and
	the scraper. This allows us to save each review to the db as it
	is found without keeping it in memory.

	"""
	review_fail_log = "Review @ '{}' unable to be created, skipping"

	for group_page in _get_review_group_pages(last_ran, start_page=start_page):
		for review_url in _get_review_urls(group_page, last_ran):
			#self.response = requests.get(
			#	review_url, headers=headers)
			response = _get_response(review_url)

			review_html = response.content
			soup = BeautifulSoup(review_html, 'html.parser')

			# Find div for multiple albums if it exists 
			multiple_albums = soup.find(
				'div', 
				{'class':'multi-tombstone-widget'})	
			if(multiple_albums == None): # If one album
				try:
					yield Review(review_html, review_url)
				except AttributeError:
					logger.error(
						review_fail_log.format(
						review_url))
					continue
			else: 
				# Get individual albums
				review_tags = soup.find_all(
					'div', {
						'class':
						'single-album-tombstone'
						}
					)
				# Make review object from individual tag
				for review in review_tags:
					try:
						yield Review(
							str(review), 
							review_url)
					except AttributeError:
						logger.error(review_fail_log.format(
							review_url))
						continue

def _get_review_group_pages(last_ran, start_page=1):
	""" 
	This function goes through the pages starting at 
	https://pitchfork.com/reviews/albums/?page=1 and iteratively 
	returns the soup object of pages that contain unprocessed 
	reviews. 
	"""
	review_url_base = BASE_URL + '/reviews/albums/?page='	

	for page_number in count(start=start_page):# Loop start_page -> inf
		logger.info("Page {} being scraped".format(page_number))
		reviews_url = review_url_base + str(page_number)
		#self.response = requests.get(self.reviews_url, 
		#				headers=headers)
		response = _get_response(reviews_url)
		page = BeautifulSoup(
			response.content, 'html.parser')
	
		# Find most recent review on page
		time_tag = page.find('time')
		if(time_tag == None):
			logger.warn("Unable to find date on page," \
			+ "testing date on per review basis for" \
			+ "page '{}'".format(reviews_url))
			yield page	
		else:
			
			datetime_str = time_tag['datetime']
			datetime_obj = datetime.strptime(
						datetime_str, 
						DATE_FORMAT)
			if(last_ran < datetime_obj):
				yield page 
			else:
				raise StopIteration	

def _get_review_urls(page, last_ran):
	"""
	Given a soup object of a page containing a list of reviews, 
	for example the html on: 
	https://pitchfork.com/reviews/albums/?page=1, iteratively 
	return the url of the reviews on that page that have been
	posted since the last time the script was run.
	"""

	reviews = page.find_all("div", {"class": "review"})
	for review in reviews :
		review_dttm_str = review.time['datetime']
		review_dttm_obj = datetime.strptime(
						review_dttm_str,
						DATE_FORMAT) 
		if(review_dttm_obj > last_ran) :
			url_tag = review.find(('a', 
					{'class':'album-link'}))
			url = BASE_URL + url_tag['href']
			yield url		
		else:
			raise StopIteration	

def _get_response(url):
	try:
		response = requests.get(
			url, headers=headers)
	except requests.exceptions.RequestException as e:
		logger.error(e)
		logger.info("URL request exception caught, retrying")
		retry = "Y"
		success = False
		while( (retry in ['y', 'Y']) and not success):
			try:
				response = requests.get(url, 
					headers=headers)
				retry = 'n'
				success = True

			except requests.exceptions.RequestException:
				logger.info("URL request retry failed")
				retry = input("Retry the request again? (Y/N):")	
				continue
	return response


scraper()
