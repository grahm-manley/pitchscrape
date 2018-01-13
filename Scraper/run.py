from scraper import Scraper
from db_connection import DbConnection
import time
from datetime import datetime

fails = []
with DbConnection() as db:
	scrape = Scraper(db.get_last_update_time())
	saved_reviews = 0
	for review in scrape.get_unsaved_reviews():
		print('Scraped: ', review.album_title, ' by ', review.artists)
		try:
			if(db.save_review(review)):
				saved_reviews = saved_reviews + 1
		except Exception as e:
			print('Failed to save : ', review.album_title)
			print('--------- Exception ----------------')
			print(e)
			print('------------------------------------')
			fails.append((review.album_title, review.artists))
			
		time.sleep(1)	

print("SCRAPE COMPLETED @ {}: Saved {} reviews with {} errors".format(
	datetime.now(), saved_reviews, len(fails))) 
