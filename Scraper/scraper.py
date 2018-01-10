from itertools import count
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from review import Review

headers = {'User-Agent':'Mozilla/5.0'}
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
BASE_URL = 'https://pitchfork.com' 
# LAST_RAN date is a placeholder until it is setup to pull the date from the DB
LAST_RAN = datetime.today() - timedelta(days=5)

class Scraper:
	def __init__(self, last_ran):
		self.last_ran = last_ran

	def get_unsaved_reviews(self):
		"""
		Retrieve the reviews that have been added to pitchfork since 
		the program was last ran. The function is a generator to allow 
		for separation between the class dealing with the database and
		the scraper. This allows us to save each review to the db as it
		is found without keeping it in memory.

		"""
		for group_page in self._get_review_group_pages():
			for review_url in self._get_review_urls(group_page):
				self.response = requests.get(
					review_url, headers=headers)
				self.review_html = self.response.content
				self.soup = BeautifulSoup(self.review_html, 
							'html.parser')

				# Find div for multiple albums if it exists 
				self.multiple_albums = self.soup.find(
					'div', 
					{'class':'multi-tombstone-widget'})	
				if(self.multiple_albums == None): # If one album
					yield Review(self.review_html)
				else: 
					# Get individual albums
					self.review_tags = self.soup.find_all(
						'div', {
							'class':
							'single-album-tombstone'
							}
						)
					# Make review object from individual tag
					for review in self.review_tags:
						yield Review(str(review))
			

	def _get_review_group_pages(self):
		""" 
		This function goes through the pages starting at 
		https://pitchfork.com/reviews/albums/?page=1 and iteratively 
		returns the soup object of pages that contain unprocessed 
		reviews. 
		"""
		self.review_url_base = BASE_URL + '/reviews/albums/?page='	

		for page_number in count(start=1): 	# Loop 1 -> inf
			self.reviews_url = self.review_url_base + str(page_number)
			self.response = requests.get(self.reviews_url, 
							headers=headers)
			self.page = BeautifulSoup(
				self.response.content, 'html.parser')
		
			# Find most recent review on page
			self.time_tag = self.page.find('time')
			self.datetime_str = self.time_tag['datetime']
			self.datetime_obj = datetime.strptime(self.datetime_str, 
							DATE_FORMAT)
			if(self.last_ran < self.datetime_obj):
				yield self.page 
			else:
				raise StopIteration	

	def _get_review_urls(self, page):
		"""
		Given a soup object of a page containing a list of reviews, 
		for example the html on: 
		https://pitchfork.com/reviews/albums/?page=1, iteratively 
		return the url of the reviews on that page that have been
		posted since the last time the script was run.
		"""

		self.reviews = page.find_all("div", {"class": "review"})
		for review in self.reviews :
			self.review_dttm_str = review.time['datetime']
			self.review_dttm_obj = datetime.strptime(
							self.review_dttm_str,
							DATE_FORMAT) 
			if(self.review_dttm_obj > self.last_ran) :
				self.url_tag = review.find(('a', 
						{'class':'album-link'}))
				self.url = BASE_URL + self.url_tag['href']
				yield self.url		
			else:
				raise StopIteration	
