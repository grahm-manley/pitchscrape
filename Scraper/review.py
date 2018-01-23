from bs4 import BeautifulSoup 

class Review(object):

	def __init__(self, html, url):
		self.html = html
		self.url = url
		self.soup = BeautifulSoup(self.html, 'html.parser')
		
		self._set_album_title()
		self._set_artists()
		self._set_score()

	def _set_album_title(self):
		self.album_title_tag = self.soup.find('h1',
				{'class':
				'single-album-tombstone__review-title'})
		self.album_title = self.album_title_tag.text

	def _set_artists(self):
		self.artists_tag = self.soup.find('ul', 
			{'class':
			'artist-links artist-list single-album-tombstone__artist-links'})
		self.artist_tag_list = self.artists_tag.find_all('a')
		self.artists = [artist.text for artist in self.artist_tag_list]


	def _set_score(self):
		self.score = (self.soup.find('span', {'class':'score'})).text
