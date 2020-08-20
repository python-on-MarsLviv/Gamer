import json
from os import mkdir
from os import getcwd
from os.path import join
from os.path import exists
from time import time

import logging.config
from logger import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')

class ConfigParams(object):
	''' class singelton to manage configuration '''

	# write default information into fields
	data = []
	data.append({
	    "version": 0.1,
	    "user_name": "user",
	    "game": "Click-Click",
	    "delay": 1.1,
	    "increase_latancy": 1,
	    "keep_log_file_days": 3,
	    "path_to_log_file": "log/"
		})

	def __new__(cls):
		''' ensure just one instance of this class '''
		if not hasattr(cls, 'instance'):
			cls.instance = super(ConfigParams, cls).__new__(cls)
			cls.instance.config_file(file='config.json')
		return cls.instance

	def config_save(self, file='config.json'):
		''' save configratoion info'''
		try:
			with open(file, 'w') as f:
				ConfigParams.data[0]['HELP game'] = 'Value in [Twins, Click-Click, Count color, Count colors, Find number, Find object]'
				ConfigParams.data[0]['HELP delay'] = 'Value in [0:0.1:5]'
				ConfigParams.data[0]['HELP increase_latancy'] = 'Value in [0 1]'
				ConfigParams.data[0]['HELP keep_log_file_days'] = 'Value in [1 .. 365]'
				ConfigParams.data[0]['HELP path_to_log_file'] = 'path to log file'
				json.dump(ConfigParams.data[0], f, indent=4)
		except:
			logger.info('Could not save configuration file.')

	def config_file(self, file='config.json'):
		''' format configratoion info'''
		try:
			with open(file, 'r') as f:
				ConfigParams.data.append(json.load(f))
		except:
			logger.info('Could not load configuration file. Using default parameters.')
			return
		
		# parse all keys
		if ConfigParams.data[1]['game'] in ['Twins', 'Click-Click', 'Count color', 'Count colors', 'Find number', 'Find object']:
			ConfigParams.data[0]['game'] = ConfigParams.data[1]['game']
		if ConfigParams.data[1]['delay'] >= 0 and ConfigParams.data[1]['delay'] <= 5:
			ConfigParams.data[0]['delay'] = ConfigParams.data[1]['delay']
		if ConfigParams.data[1]['increase_latancy'] in [0, 1]:
			ConfigParams.data[0]['increase_latancy'] = ConfigParams.data[1]['increase_latancy']
		if ConfigParams.data[1]['keep_log_file_days'] >= 1 and ConfigParams.data[1]['keep_log_file_days'] <= 365:
			ConfigParams.data[0]['keep_log_file_days'] = ConfigParams.data[1]['keep_log_file_days']

		self.make_dir(ConfigParams, 'path_to_log_file')
		
	def make_dir(self, ConfigParams, dir):
		''' creates drectory <dir> if not exist and write it to configuration '''
		path = join(getcwd(), ConfigParams.data[1][dir])
		if exists(path):
			ConfigParams.data[0][dir] = path
		else:
			try:
				mkdir(path)
				ConfigParams.data[0][dir] = path
			except OSError:
				logger.info('Creation of the directory {} failed. Try use name with timestamp.'.format(path))
				path = join(path, '_', str(int(time())))
				mkdir(path)
				ConfigParams.data[0][dir] = path
			except:
				logger.info('Creation of the directory {} failed. Exiting.'.format(path))

# can be tested to convince it Singelton
# usage: python config_params.py
if __name__ == "__main__":
	s = ConfigParams()
	s1 = ConfigParams()

	s.data[0]['user_name'] = '100'
	print(s.data[0]['user_name'])
	print(s1.data[0]['user_name'])
		

