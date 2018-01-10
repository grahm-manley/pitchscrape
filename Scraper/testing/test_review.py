import sys
sys.path.append('..')
import review

file = open('html/review_test1.html')
page = file.read()
file.close()

def test_album_title():
	review1 = review.Review(page)	
	assert(review1.artists[0] == 'Wilco')
	assert(review1.album_title == 'Yankee Hotel Foxtrot')	
	assert(review1.score == '10')
