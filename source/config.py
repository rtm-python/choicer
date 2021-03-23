# -*- coding: utf-8 -*-

"""
Configuration module to define application variables and constants.
"""

# Standard libraries import
import os
import sys
import json
import logging
from enum import Enum

# Environment value keys
CONFIG_PATH_KEY = 'APP_CONFIG_PATH'
LOCALE_PATH_KEY = 'APP_LOCALE_PATH'

# Configuration constants
CONFIG_PATH = 'config/app.json'
LOCALE_PATH = 'source/locale.json'
STATIC_PATH = 'source/static'
TEMPLATE_PATH = 'source/templates'
DATABASE_PATH = 'database'
DATABASE_FILES_PATH = 'database/files'
TEMPORARY_PATH = 'temporary'


def define_from(environ_key: str, default_path: str) -> dict:
	"""
	Return dictionary from json-file
	defined by environment key or default path.
	"""
	try:
		if not os.path.isfile(os.environ.get(environ_key, default_path)):
			raise ValueError('Define %s error!' % environ_key)
		with open(os.environ.get(environ_key, default_path), 'r') as file:
			return json.loads(file.read())
	except Exception as exc:
		logging.error(getattr(exc, 'message', repr(exc)))
		sys.exit(0)


# Define configuration and localization
CONFIG = define_from(CONFIG_PATH_KEY, CONFIG_PATH)
LOCALE = define_from(LOCALE_PATH_KEY, LOCALE_PATH)
logging.basicConfig(format=CONFIG.get('logging'), level=logging.ERROR)


def define_list(folder: str, extension: str) -> list:
	"""
	Return list of filenames from folder with defined extension.
	"""
	try:
		if not os.path.exists(folder):
			raise ValueError('Define %s error!' % folder)
		result = []
		for filename in os.listdir(folder):
			if filename.endswith(extension):
				result += [filename]
		return result
	except Exception as exc:
		logging.error(getattr(exc, 'message', repr(exc)))
		sys.exit(0)
