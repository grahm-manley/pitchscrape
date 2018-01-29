import logging

logging_config = dict(
	version = 1,
	handlers = {
		'ch' : {'class': 'logging.StreamHandler',
			'level':logging.INFO},
		'fh' : {'class': 'logging.FileHandler',
			'filename':'scrape_run.log',
			'level':logging.INFO}
	},
	root = {
		'handlers':['ch','fh'],
		'level':logging.INFO
	},
)

DB_CONFIG = {
	'host': 'localhost',
	'user':'root',
	'passwd':'1234',
	'db':'pitch1'
}
