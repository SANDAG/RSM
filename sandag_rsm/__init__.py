try:
	from .logging import logging_start
	logging_start(20)

except:
	pass #doesn't work with python 2