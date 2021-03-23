# -*- coding: utf-8 -*-

"""
Main module to run application.
"""

# Standard libraries import
import logging
import sys
import os

# Append source path on wsgi initialization
sys.path.append('source')

# Application moudles import
from blueprints import application
from models import database
from config import CONFIG
from plugins import PluginManager


@application.cli.command('run-identica')
def run_identica():
	"""
	Run PluginManager to communicate with application identica bot.
	"""
	logging.basicConfig(format=CONFIG.get('logging'), level='INFO')
	PluginManager(
		'identica', domain_url='http://192.168.44.150:5000').execute('run')


@application.cli.command('run-admin')
def run_admin():
	"""
	Run PluginManager to administrate application.
	"""
	logging.basicConfig(format=CONFIG.get('logging'), level='INFO')
	source_path = os.path.dirname(__file__)
	PluginManager('admin', source_path=source_path).execute('configure')


if __name__ == '__main__':
	adhoc = None
	logging.basicConfig(format=CONFIG.get('logging'), level='DEBUG')
	application.run(
		host=CONFIG.get('host'), port=CONFIG.get('port'),
		threaded=True, ssl_context=adhoc, debug=True
	)
