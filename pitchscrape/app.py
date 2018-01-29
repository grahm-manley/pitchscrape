from flask import Flask, jsonify, make_response
from core import db_connection

app = Flask(__name__)

@app.route('/<string:artist>/<string:album>', methods=['GET'])
def get_review(artist, album):
	with db_connection.DbConnection() as db:
		review = db.get_review([artist], album)
		if(review is None):
			return not_found(None)
		else:
			review_json = review.jsonify()
			return review_json

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error':'Not found'}), 404)

if __name__ == '__main__':
	app.run(debug=True)

