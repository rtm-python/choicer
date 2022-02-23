# -*- coding: utf-8 -*-

"""
Module to handle plugin manager.
"""

# Standard libraries import
import os
import json
import uuid
import time
import logging
import secrets
import string

# Additional libraries import
import requests

# Application constants
CHOICER_PATH = os.path.dirname(__file__)
CHOICER_JSON = 'choicer.json'
POLL_FILE_EXT = '.poll'
VOTE_FILE_EXT = '.vote'
IMGS_FILE_EXT = '.imgs'
LANGUAGES = ['en', 'ru']
MESSAGES = [
	{
		'en': 'Use keyboard to select command',
		'ru': 'Используйте клавиватуру для выбора команды'
	},
	{
		'en': 'There are no active polls',
		'ru': 'Нет активных голосований'
	},
	{
		'en': 'Make your choice',
		'ru': 'Сделайте свой выбор'
	},
	{
		'en': 'Vote accepted',
		'ru': 'Голос принят'
	},
	{
		'en': 'Vote previously already accepted',
		'ru': 'Голос уже принят ранее'
	},
	{
		'en': 'Update results',
		'ru': 'Обновить результаты'
	}
]
KEYBOARDS = [
	[
		[
			{
				'id': '/poll',
				'title': {
					'en': 'Request Poll',
					'ru': 'Запросить голосование'
				}
			}
		]
	]
]
# Initiate pseudo commands for keyboards
PSEUDO_COMMANDS = {}
for keyboard in KEYBOARDS:
	for button in keyboard:
		for key, value in button[0]['title'].items():
			PSEUDO_COMMANDS[value] = button[0]['id']
LOOP_TIMEOUT = 1
REQUEST_TIMEOUT = (3.0, 15.0)


class Plugin():
	"""
	This Plugin class describes managing process
	on identica bot communication.
	"""
	config_filename = None
	config = None
	offset = 0

	def __init__(self) -> "Plugin":
		"""
		Inititate Plugin object with configuration data.
		"""
		self.config_filename = os.path.join(CHOICER_PATH, CHOICER_JSON)
		if not self.init_config():
			raise ValueError('Initiate Error!')
		logging.debug('Choicer initiated')

	def init_config(self) -> bool:
		"""
		Initiate configuration.
		"""
		# Read out configuration from file
		if not os.path.isfile(self.config_filename):
			logging.error('Configuration not found!')
			return
		with open(self.config_filename, 'r') as file:
			self.config = json.loads(file.read())
		with open(self.config_filename, 'w') as file:
			file.write('')
		os.remove(self.config_filename)
		# Initiate configuration
		self.config['bot_url']['setMyCommands'] = \
			self.config['bot_url']['setMyCommands'] % self.config['token']
		self.config['bot_url']['getUpdates'] = \
			self.config['bot_url']['getUpdates'] % self.config['token'] + \
			self.config['bot_url']['getUpdatesArguments']
		self.config['bot_url']['sendMessage'] = \
			self.config['bot_url']['sendMessage'] % self.config['token']
		self.config['bot_url']['editMessageText'] = \
			self.config['bot_url']['editMessageText'] % self.config['token']
		self.config['bot_url']['sendPhoto'] = \
			self.config['bot_url']['sendPhoto'] % self.config['token']
		self.config['bot_url']['deleteMessage'] = \
			self.config['bot_url']['deleteMessage'] % self.config['token']
		self.config['bot_url']['answerCallbackQuery'] = \
			self.config['bot_url']['answerCallbackQuery'] % self.config['token']
		# Initiate update message (ignore previous)
		response = requests.get(
			self.config['bot_url']['getUpdates'] % (-1, 1),
			timeout=REQUEST_TIMEOUT
		)
		if not response.json()['ok']:
			logging.error('Initiate update message error')
			return
		self.offset = response.json()['result'][0]['update_id'] + 1 \
			if response.json()['result'] else 0
		# Initiate logging
		if self.config.get('logging'):
			logging.basicConfig(
				format=self.config['logging'].get('format'),
				level=self.config['logging'].get('level')
			)
		logging.getLogger('requests').setLevel(logging.INFO)
		logging.getLogger('urllib3').setLevel(logging.INFO)
		logging.debug('Choicer configuration initiated')
		return True

	def run(self) -> None:
		"""
		Run infinite loop to manage communication through files in folder.
		"""
		try:
			result = True
			logging.debug('Choicer start main loop')
			while True:
				try:
					if not result and os.path.isfile(self.config_filename):
						self.init_config() # Read config if read not True
						result = True
					response = requests.get(
						self.config['bot_url']['getUpdates'] % (self.offset, 25),
						timeout=REQUEST_TIMEOUT
					)
					if not response.json()['ok']:
						logging.error('Get updates error (offset = %d): %s' % \
													(self.offset, response.json()))
						result = False
						continue
					for item in response.json()['result']:
						# Define offset for updates
						if self.offset <= item['update_id']:
							self.offset = item['update_id'] + 1
						# Handle updates (message or callback)
						if item.get('message'):
							if not self.handle_message(item['message']):
								result = False
						elif item.get('callback_query'):
							if not self.handle_callback(item['callback_query']):
								result = False
				except KeyboardInterrupt:
					break
				except:
					logging.error('Error while running', exc_info=1)
				time.sleep(LOOP_TIMEOUT) # Prevent overhead
		except KeyboardInterrupt:
			pass
		logging.debug('Choicer stop main loop')

	def handle_message(self, message: dict) -> bool:
		"""
		Handle message and return True on success.
		"""
		if message['from']['is_bot']:
			logging.warning(
				'Ignoring message from bot: %s' % \
				 message['from']['id']
			)
			return True # Ignore bot messages
		language = message['from'].get('language_code') \
			if message['from'].get('language_code') in LANGUAGES else 'en'
		if message['text'] == '/start':
			response = self.send_keyboard(
				message['chat']['id'],
				language, KEYBOARDS[0], False
			)
		pseudo_command = PSEUDO_COMMANDS.get(message['text'])
		if pseudo_command == '/poll':
			poll_data = None
			for filename in os.listdir(CHOICER_PATH):
				if filename.endswith(POLL_FILE_EXT):
					poll_uid = filename[:len(filename) - 5]
					with open(os.path.join(CHOICER_PATH, filename), 'r') as file:
						poll_data = json.loads(file.read())
					break
			if poll_data is None:
				response = requests.get(
					self.config['bot_url']['sendMessage'],
					json={
						'chat_id': message['chat']['id'],
						'text': MESSAGES[1][language]
					},
					timeout=REQUEST_TIMEOUT
				).json()
				return True
			response = self.send_poll(
				message['chat']['id'], language, poll_uid, poll_data
			)
		else:
			return True
		if not response['ok']:
			logging.error(response)
			return False
		return True

	def handle_callback(self, callback: dict) -> bool:
		"""
		Handle callback and return True on success.
		"""
		if callback['from']['is_bot']:
			logging.warning(
				'Ignoring message from bot: %s' % \
				 callback['from']['id']
			)
			return True # Ignore bot callbacks
		language = callback['from'].get('language_code') \
			if callback['from'].get('language_code') in LANGUAGES else 'en'
		if '-option-' in callback['data']:
			poll_uid, option_index = callback['data'].split('-option-')
			vote_filename = os.path.join(CHOICER_PATH, poll_uid + VOTE_FILE_EXT)
			if not os.path.isfile(vote_filename):
				response = requests.get(
					self.config['bot_url']['answerCallbackQuery'],
					json={
						'callback_query_id': callback['id'],
						'text': 'Fail'
					},
					timeout=REQUEST_TIMEOUT
				).json()
				return True
			with open(vote_filename, 'r') as file:
				vote_data = json.loads(file.read())
			from_id = str(callback['from']['id'])
			if vote_data['voters']['vote'].get(from_id) is not None:
				# already voted user
				response = requests.get(
					self.config['bot_url']['answerCallbackQuery'],
					json={
						'callback_query_id': callback['id'],
						'text': 'Fail'
					},
					timeout=REQUEST_TIMEOUT
				).json()
				option_index = vote_data['voters']['vote'][from_id]
				response = requests.get(
					self.config['bot_url']['sendMessage'],
					json={
						'chat_id': callback['message']['chat']['id'],
						'text': '%s: %s' % (
							MESSAGES[4][language],
							vote_data['results'][option_index]['title']
						)
					},
					timeout=REQUEST_TIMEOUT
				).json()
				return True
			# response success callback
			response = requests.get(
				self.config['bot_url']['answerCallbackQuery'],
				json={
					'callback_query_id': callback['id'],
					'text': 'Success'
				},
				timeout=REQUEST_TIMEOUT
			)
			# accept vote and recalculate percents
			option_index = int(option_index)
			vote_data['results'][option_index]['count'] += 1
			vote_data['voters']['count'] += 1
			vote_data['voters']['vote'][from_id] = option_index
			total = 100
			min_percent = 100
			min_index = 0
			for index, option in enumerate(vote_data['results']):
				option['percent'] = \
						100 * option['count'] // vote_data['voters']['count']
				total -= option['percent']
				if option['percent'] > 0 and option['percent'] < min_percent:
					min_percent = option['percent']
					min_index = index
			if total > 0:
				vote_data['results'][min_index]['percent'] += total
			with open(vote_filename, 'w') as file:
				file.write(json.dumps(vote_data))
			response = self.send_results(
				callback['message']['chat']['id'], poll_uid,
				None, language, vote_data, option_index
			)
		elif '-results-' in callback['data']:
			poll_uid, message_id = callback['data'].split('-results-')
			vote_filename = os.path.join(CHOICER_PATH, poll_uid + VOTE_FILE_EXT)
			if not os.path.isfile(vote_filename):
				response = requests.get(
					self.config['bot_url']['answerCallbackQuery'],
					json={
						'callback_query_id': callback['id'],
						'text': 'Fail'
					},
					timeout=REQUEST_TIMEOUT
				).json()
				return True
			# response success callback
			response = requests.get(
				self.config['bot_url']['answerCallbackQuery'],
				json={
					'callback_query_id': callback['id'],
					'text': 'Success'
				},
				timeout=REQUEST_TIMEOUT
			)
			# send results from vote file
			with open(vote_filename, 'r') as file:
				vote_data = json.loads(file.read())
			response = self.send_results(
				callback['message']['chat']['id'], poll_uid,
				int(message_id), language, vote_data, None
			)
		else: # Ignore other callbacks
			response = requests.get(
				self.config['bot_url']['answerCallbackQuery'],
				json={
					'callback_query_id': callback['id'],
					'text': 'Fail'
				},
				timeout=REQUEST_TIMEOUT
			)
			return True
		if not response['ok']:
			logging.error(response)
			return False
		return True

	def set_commands(self) -> dict:
		"""
		Set commands and return response dictionary.
		"""
		return requests.get(
			self.config['bot_url']['setMyCommands'],
			json={ 'commands': COMMANDS },
			timeout=REQUEST_TIMEOUT
		).json()

	def send_keyboard(self, chat_id: str,
										language: str, keyboard: list,
										use_website: bool = True) -> dict:
		"""
		Send keyboard to user within chat message
		and return response dictionary.
		"""
		return requests.get(
			self.config['bot_url']['sendMessage'],
			json={
				'chat_id': chat_id,
				'text': MESSAGES[0][language],
				'reply_markup':{
					'keyboard': [
						[
							{
								'text': button[0]['title'][language]
							}
						] for button in keyboard
					]
				}
			},
			timeout=REQUEST_TIMEOUT
		).json()

	def send_photo(self, chat_id: str, poll_uid: str,
								 image: dict, caption: str,
								 inline_keyboard = None) -> dict:
		"""
		Send photo within chat message.
		"""
		if image is None or image['filepath'] is None:
			return None
		msg_data = { 'chat_id': chat_id, 'caption': caption }
		reply_markup = { 'inline_keyboard': inline_keyboard } \
			if inline_keyboard is not None else {}
		# load imgs data to send file_id for previously uploaded photo
		imgs_filename = os.path.join(CHOICER_PATH, poll_uid + IMGS_FILE_EXT)
		with open(imgs_filename, 'r') as file:
			imgs_data = json.loads(file.read())
		photo = imgs_data.get(image['filepath'])
		if photo is not None: # previously uploaded photo present with file_id
			msg_data['photo'] = photo['file_id']
			response = requests.get(
				self.config['bot_url']['sendPhoto'],
				json={ **msg_data, 'reply_markup': reply_markup },
				timeout=REQUEST_TIMEOUT
			)
			return photo
		with open(image['filepath'], 'rb') as file: # upload photo and store photo with file_id
			response = requests.get(
				self.config['bot_url']['sendPhoto'], files={ 'photo': file },
				params={ **msg_data, 'reply_markup': json.dumps(reply_markup) },
				timeout=REQUEST_TIMEOUT
			).json()
			if response['ok']:
				photo = response['result']['photo'][0]
			else:
				print(response)
		if photo is not None: # photo successfully uploaded
			imgs_data[image['filepath']] = photo
			with open(imgs_filename, 'w') as file:
				file.write(json.dumps(imgs_data))
		return photo

	def send_poll(self, chat_id: str, language: str,
								poll_uid: str, poll_data: dict) -> dict:
		"""
		Send poll within chat message with callback on options.
		"""
		inline_keyboard = [
			[
				{
					'text': option['title'],
					'callback_data': '%s-option-%d' % (poll_uid, index)
				}
			] for index, option in enumerate(poll_data['options'])
		]
		message = ', '.join(
			[ poll_data['title'] or '', poll_data['description'] or '' ]
		)
		photo = self.send_photo(chat_id, poll_uid, poll_data['image'], message)
		if photo is None:
			response = requests.get(
				self.config['bot_url']['sendMessage'],
				json={ 'chat_id': chat_id, 'text': message },
				timeout=REQUEST_TIMEOUT
			)
		for index, option in enumerate(poll_data['options']):
			inline_keyboard = [
				[
					{
						'text': option['title'],
						'callback_data': '%s-option-%d' % (poll_uid, index)
					}
				]
			]
			message = ', '.join([ option['title'] or '', option['description'] or '' ])
			photo = self.send_photo(
				chat_id, poll_uid, option['image'], message, inline_keyboard)
			if photo is None:
				response = requests.get(
					self.config['bot_url']['sendMessage'],
					json={
						'chat_id': chat_id, 'text': message,
						'reply_markup': { 'inline_keyboard': inline_keyboard }
					},
					timeout=REQUEST_TIMEOUT
				)
		return requests.get(
			self.config['bot_url']['sendMessage'],
			json={
				'chat_id': chat_id,
				'text': MESSAGES[2][language]
			},
			timeout=REQUEST_TIMEOUT
		).json()

	def send_results(self, chat_id: str, poll_uid: str, message_id: int,
									 language: str, vote_data: dict, option_index: int) -> dict:
		"""
		Send poll's results within chat message with callback to update.
		"""
		results = '\r\n'.join(
			[
				'<strong>%s</strong> - %d%%' % (
					option['title'], option['percent']
				) for option in vote_data['results']
			]
		)
		if message_id is None:
			response = requests.get(
				self.config['bot_url']['sendMessage'],
				json={
					'chat_id': chat_id,
					'text': results,
					'parse_mode': 'HTML'
				},
				timeout=REQUEST_TIMEOUT
			).json()
			if not response['ok']:
				logging.error(response)
				return response
			if option_index is None:
				return response
			message_id = int(response['result']['message_id'])
			inline_keyboard = [
				[
					{
						'text': MESSAGES[5][language],
						'callback_data': '%s-results-%d' % (poll_uid, message_id)
					}
				]
			]
			return requests.get(
				self.config['bot_url']['sendMessage'],
				json={
					'chat_id': chat_id,
					'text': '%s: %s' % (
						MESSAGES[3][language],
						vote_data['results'][option_index]['title']
					),
					'reply_markup': { 'inline_keyboard': inline_keyboard }
				},
				timeout=REQUEST_TIMEOUT
			).json()
		else:
			return requests.get(
				self.config['bot_url']['editMessageText'],
				json={
					'chat_id': chat_id,
					'message_id': message_id,
					'text': results,
					'parse_mode': 'HTML'
				},
				timeout=REQUEST_TIMEOUT
			).json()

	def send_callback(self, chat_id: str, message: str,
							 			options: list) -> dict:
		"""
		Send website link button to user within chat message
		and return response dictionary.
		"""
		inline_keyboard = [
			[
				{ 'text': option, 'callback_data': option }
			] for option in options
		]
		return requests.get(
			self.config['bot_url']['sendMessage'],
			json={
				'chat_id': chat_id,
				'text': message,
				'reply_markup':{
					'inline_keyboard': inline_keyboard
				}
			},
			timeout=REQUEST_TIMEOUT
		).json()

	@staticmethod
	def play_poll(poll_data: dict, vote_data: dict) -> str:
		"""
		Create poll file and return generated poll's uid.
		"""
		poll_data['active'] = True
		uid = str(uuid.uuid4())
		poll_filename = os.path.join(CHOICER_PATH, uid + POLL_FILE_EXT)
		with open(poll_filename, 'w') as file:
			file.write(json.dumps(poll_data))
		if vote_data is None:
			vote_data = {
				'results': [
					{
						'title': option['title'],
						'image': option['image'],
						'count': 0,
						'percent': 0
					} for option in poll_data['options']
				],
				'voters': {
					'count': 0,
					'vote': {} # {from_id: options_index}
				}
			}
		vote_filename = os.path.join(CHOICER_PATH, uid + VOTE_FILE_EXT)
		with open(vote_filename, 'w') as file:
			file.write(json.dumps(vote_data))
		imgs_filename = os.path.join(CHOICER_PATH, uid + IMGS_FILE_EXT)
		with open(imgs_filename, 'w') as file:
			file.write(json.dumps({}))
		return uid

	@staticmethod
	def read_poll(poll_uid: str) -> dict:
		"""
		Read poll data from files.
		"""
		poll_filename = os.path.join(CHOICER_PATH, poll_uid + POLL_FILE_EXT)
		with open(poll_filename, 'r') as file:
			poll_data = json.loads(file.read())
		vote_filename = os.path.join(CHOICER_PATH, poll_uid + VOTE_FILE_EXT)
		with open(vote_filename, 'r') as file:
			vote_data = json.loads(file.read())
		return {**poll_data, **vote_data}

	@staticmethod
	def stop_poll(poll_uid: str) -> dict:
		"""
		Update poll file with setting active to False (visible as inactive),
		wait for double loop timeout, remove files and return poll data.
		"""
		poll_filename = os.path.join(CHOICER_PATH, poll_uid + POLL_FILE_EXT)
		vote_filename = os.path.join(CHOICER_PATH, poll_uid + VOTE_FILE_EXT)
		imgs_filename = os.path.join(CHOICER_PATH, poll_uid + IMGS_FILE_EXT)
		try:
			with open(poll_filename, 'r') as file:
				poll_data = json.loads(file.read())
			poll_data['active'] = False
			with open(poll_filename, 'w') as file:
				file.write(json.dumps(poll_data))
			for i in range(2):
				time.sleep(LOOP_TIMEOUT)
			with open(vote_filename, 'r') as file:
				vote_data = json.loads(file.read())
			poll_data = {**poll_data, **vote_data}
		except FileNotFoundError:
			poll_data = None
		if os.path.isfile(poll_filename):
			os.remove(poll_filename)
		if os.path.isfile(vote_filename):
			os.remove(vote_filename)
		if os.path.isfile(imgs_filename):
			os.remove(imgs_filename)
		return poll_data

	@staticmethod
	def free_poll() -> str:
		"""
		Return currently active poll's uid.
		"""
		for filename in os.listdir(CHOICER_PATH):
			if filename.endswith(POLL_FILE_EXT):
				return filename[: len(filename) - 5]