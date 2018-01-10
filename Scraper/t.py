import db_connection 
from unittest.mock import patch

class review_mock:
	def __init__(self):
		self.album_title = 'My Album'
		self.score = '5.5'
		self.url = 'somelink.com'
		self.artists = ['first artist', 'second artist']
"""
db_help = db_helper.DbHelper()
db_help.save_review(review_mock())
print(db_help.get_last_update_time())
db_help.close()
"""
with db_connection.DbConnection() as db:
	db.save_review(review_mock())
