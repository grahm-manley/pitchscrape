import MySQLdb
import datetime
import warnings
import logging
from . import config
from . import review

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class DbConnection:

	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.db = MySQLdb.connect(
				host=config.DB_CONFIG['host'],
				user=config.DB_CONFIG['user'],
				passwd=config.DB_CONFIG['passwd'],
				db=config.DB_CONFIG['db']
				)
		self.db.set_character_set('utf8')
		self.cur = self.db.cursor()
		self.cur.execute('SET NAMES utf8;')
		self.cur.execute('SET CHARACTER SET utf8;')
		self.cur.execute('SET character_set_connection=utf8;')
		
		self._create_tables()

	def get_review(self, artists, album):
		""" 
		Given a list of artists and an album name, return an object
		of the review if it exists and a null object othherwise
		"""
		if(len(artists) != 0): # Check if review has artists
			self.sql = """
				SELECT r.album_title, r.url, r.score 
				FROM review r, artist a
				WHERE r.id = a.review_id
				AND r.album_title = %s
				AND a.artist = %s;
				"""
			self.cur.execute(self.sql, [album, artists[0]])
		else:
			self.sql = """
				SELECT r.album_title, r.url, r.score
				FROM review r 
				WHERE r.album_title = %s; 
				"""
			self.cur.execute(self.sql, [album])
		if(self.cur.rowcount > 0): # If review exists
			row = self.cur.fetchone()
			return review.Review(None, row[1], row[0], artists, row[2]) 
		else:
			return None
						


	def save_review(self, review):
		"""
		Given a review, save it to the database.
		Return True if it was successfully inserted
		"""
		
		# Check if record already exists
		if(len(review.artists) != 0): # Check if review has artists
			self.sql = """
				SELECT * FROM review r, artist a
				WHERE r.id = a.review_id
				AND r.album_title = %s
				AND a.artist = %s;
				"""
			self.cur.execute(self.sql, [review.album_title, review.artists[0]])
		else:
			self.sql = """
				SELECT * FROM review r 
				WHERE r.album_title = %s; 
				"""
			self.cur.execute(self.sql, [review.album_title])
		
		if(self.cur.rowcount != 0):
			self.logger.warning(("Warning: Review '{}' by '{}'" +  
			" already \n exists in DB and was not resaved").format(
				review.album_title, review.artists))
			return False

		# Insert review album title, score, and URL
		self.sql = """
			INSERT INTO review (album_title, score, url) 
			VALUES (%s, %s, %s); 			
			"""
		self.cur.execute(self.sql, [review.album_title, 
			review.score, review.url])

		# Get review ID
		self.sql = "SELECT id FROM review ORDER BY id DESC;"
		self.cur.execute(self.sql)
		self.album_id = self.cur.fetchone()[0]

		# Insert artists into artist table
		for artist in review.artists:
			self.sql = """
				INSERT INTO artist (review_id, artist)
				VALUES (%s, %s);
				"""
			self.cur.execute(self.sql, [self.album_id, artist])

		self.db.commit()
		return True

	def get_last_update_time(self):
		"""Return the last time the database was updated"""

		self.sql = "SELECT updated FROM updated ORDER BY updated DESC;"
		self.cur.execute(self.sql)
		if(self.cur.rowcount == 0):
			return datetime.datetime(1900, 1, 1)
		else: 
			return self.cur.fetchone()[0]
	
	def close(self):
		"""Close the db connection"""
		self.db.close()
	
	def update_last_run_date(self):
		"""Add entry for current time to last run database table"""

		self.now = datetime.datetime.now()
		self.now_formatted = self.now.strftime(TIME_FORMAT)
		self.sql = "INSERT INTO updated (updated) \
			VALUES ('%s');" % (self.now_formatted) 
		self.cur.execute(self.sql)
		self.db.commit()

	def _create_tables(self):
		"""Create tables in database if they do not already exist"""
		# Hide 'table already exists' warning
		self.sql = 'SET sql_notes = 0;'
		self.cur.execute(self.sql)

		# Create review table
		self.sql = """
			CREATE TABLE IF NOT EXISTS review(
		                id              INT(11) NOT NULL AUTO_INCREMENT,
			        album_title     VARCHAR(255),
				score           VARCHAR(4),
				url             VARCHAR(512),
				PRIMARY KEY(id)
		                );
		        """
		self.cur.execute(self.sql)

		# Create artist table
		self.sql = """
			CREATE TABLE IF NOT EXISTS artist(
		        	id              INT(11) NOT NULL AUTO_INCREMENT,
		        	review_id       INT(11),
		        	artist          VARCHAR(255),
		        	PRIMARY KEY (id),
		        	FOREIGN KEY (review_id) REFERENCES review(id)
		        );
	       		"""
		self.cur.execute(self.sql)
		
		# Create updated table
		self.sql = """
			CREATE TABLE IF NOT EXISTS updated(
				updated		TIMESTAMP NOT NULL,
				PRIMARY KEY (updated)
			);

			"""
		self.cur.execute(self.sql)
		
		# Re-enable warnings
		self.sql = 'SET sql_notes = 1;'
		self.cur.execute(self.sql)
	
		self.sql = """
			ALTER DATABASE %s CHARACTER SET UTF8 
			COLLATE utf8_general_ci; 
			""" % (config.DB_CONFIG['db'])
		self.cur.execute(self.sql)

		self.sql = """ 
			ALTER TABLE artist CONVERT 
			TO CHARACTER SET UTF8 COLLATE utf8_general_ci;
			"""
		self.cur.execute(self.sql)

		self.db.commit() 

		
	def __enter__(self):
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

