from bs4 import BeautifulSoup 
import logging
import json

class Review(object):

	def __init__(self, html, url, album_title = None, artists = None, score = None):
		"""Create review object either from html or from all attributes"""
		self.logger = logging.getLogger(__name__)
		
		self.html = html
		self.url = url
		self.album_title = album_title
		self.artists = artists
		self.score = score

		if(html is not None):
			self.soup = BeautifulSoup(self.html, 'html.parser')
			try:
				self._set_album_title()
				self._set_artists()
				self._set_score()
			except AttributeError as e:
				self.logger.error("Attribute Error in review init:")
				self.logger.error(e)
				raise AttributeError	

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
	
	def jsonify(self):
		"""Return a json representation of this object"""

		d = {
			'album_title': self.album_title,
			'artists': self.artists,
			'score': self.score,
			'url': self.url
		}
		return json.dumps(d)
