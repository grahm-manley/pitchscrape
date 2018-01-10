import MySQLdb

db = MySQLdb.connect(
	host="localhost",
	user="root",
	passwd="08232515",
	db="pythonspot")

cur = db.cursor()
sql = 	"""
	CREATE TABLE IF NOT EXISTS review(
		id	 	INT(11) NOT NULL AUTO_INCREMENT,
		album_title 	VARCHAR(255),
		score 		DOUBLE(2,1),
		url 		VARCHAR(512),
		PRIMARY	KEY(id)
		);
	"""
cur.execute(sql)
db.commit()
sql = 	"""
	CREATE TABLE IF NOT EXISTS artist(
		id 		INT(11) NOT NULL AUTO_INCREMENT,
		review_id 	INT(11),
		artist		VARCHAR(255),
		PRIMARY KEY (id),
		FOREIGN KEY (review_id) REFERENCES review(id)
		);
	"""
cur.execute(sql)
db.commit()
sql = "INSERT INTO review(album_title, score, url) VALUES ('title', 1.2, 'hello.com');"
cur.execute(sql)
sql = "INSERT INTO artist(review_id, artist) VALUES (1, 'Grahm God Damn Manley');"
cur.execute(sql)
db.commit()
sql = "SELECT * FROM review"
cur.execute(sql)
for row in cur.fetchall() :
	print(row[0], " ", row[1], row[2], row[3])
sql = "SELECT * FROM artist"
cur.execute(sql)
for row in cur.fetchall() :
	print(row[0], " ", row[1], " ", row[2])
"""
sql = "INSERT INTO useless(description) VALUES ('Oh Hellooo');"
cur.execute(sql)
db.commit()
cur.execute("SELECT * FROM useless")

for row in cur.fetchall() :
	print(row[0], " ", row[1])
"""
db.close()
