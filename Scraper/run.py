from scraper import Scraper
from db_connection import DbConnection
import time
from datetime import datetime
import logging
from logging.config import dictConfig
from logging_config import logging_config

# Set up logger
dictConfig(logging_config)
logger = logging.getLogger()

fails = []

with DbConnection() as db:
	scrape = Scraper(db.get_last_update_time())
	saved_reviews = 0
	for review in scrape.get_unsaved_reviews():
		logger.info('Scraped: ' +  review.album_title + 
			' by ' + str(review.artists))
		try:
			if(db.save_review(review)):
				saved_reviews = saved_reviews + 1
		except Exception as e:
			logger.error('Failed to save : ' + review.album_title)
			logger.error(e)
			fails.append((review.album_title, review.artists))
			
		time.sleep(1) # For lessening the load on pitchfork's servers	

logger.info("SCRAPE COMPLETED @ {}: Saved {} reviews with {} errors".format(
	datetime.now(), saved_reviews, len(fails))) 

if(len(fails) > 0):
	logger.info("Fails: " + str(fails))
