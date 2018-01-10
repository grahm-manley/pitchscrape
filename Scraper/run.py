from scraper import Scraper
from db_connection import DbConnection

with DbConnection() as db:
	for review in Scraper(db.get_last_update_time()).get_unsaved_reviews():
		db.save_review()	
