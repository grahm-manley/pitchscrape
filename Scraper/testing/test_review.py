import sys
sys.path.append('..')
import Review

file = open('html/review_test1.html')
page = file.read()
file.close()

def test_album_title():
	review = Review.Review(page)	
	assert(review.artists[0] == 'Wilco')
	assert(review.album_title == 'Yankee Hotel Foxtrot')	
	assert(review.score == '10')
