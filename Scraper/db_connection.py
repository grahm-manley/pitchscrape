import MySQLdb
import config
import datetime
import warnings

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class DbConnection:

	def __init__(self):
		self.db = MySQLdb.connect(
				host=config.DB_CONFIG['host'],
				user=config.DB_CONFIG['user'],
				passwd=config.DB_CONFIG['passwd'],
				db=config.DB_CONFIG['db']
				)
		self.cur = self.db.cursor()

		self._create_tables()
	

	def save_review(self, review):
		"""
		Given a review, save it to the database.
		"""
		# Insert review album title, score, and URL
		self.sql = """
			INSERT INTO review (album_title, score, url) 
			VALUES ('%s', '%s', '%s'); 			
			""" % (review.album_title, review.score, review.url)
		self.cur.execute(self.sql)

		# Get review ID
		self.sql = "SELECT id FROM review ORDER BY id DESC;"
		self.cur.execute(self.sql)
		self.album_id = self.cur.fetchone()[0]

		# Insert artists into artist table
		for artist in review.artists:
			self.sql = """
				INSERT INTO artist (review_id, artist)
				VALUES ('%d', '%s');
				""" % (self.album_id, artist)
			self.cur.execute(self.sql)

		self.db.commit()

	def get_last_update_time(self):
		""" 
		Return the last time the database was updated
		"""

		self.sql = "SELECT updated FROM updated ORDER BY updated DESC;"
		self.cur.execute(self.sql)
		if(self.cur.rowcount == 0):
			return datetime.datetime(1900, 1, 1)
		else: 
			return self.cur.fetchone()[0]
	
	def close(self):
		""" 
		Update the last updated date and close the db connection
		"""
		
		self.now = datetime.datetime.now()
		self.now_formatted = self.now.strftime(TIME_FORMAT)
		self.sql = "INSERT INTO updated (updated) \
			VALUES ('%s');" % (self.now_formatted) 
		self.cur.execute(self.sql)
		self.db.commit()

		self.db.close()

	def _create_tables(self):
		#TODO: Handle warnings with try catch
		#warnings.filterwarnings("ignore", "1050, \"Table * already exists")
			
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
		
		self.db.commit() 

		
	def __enter__(self):
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

