# -*- coding: utf-8 -*-

"""
Module to handle identica plugin.
"""

# Standard libraries import
import os
import json
import time
import logging
import secrets
import string
from datetime import datetime
from datetime import timedelta

# Additional libraries import
import requests

# Application constants
IDENTICA_PATH = os.path.dirname(__file__)
IDENTICA_JSON = 'identica.json'
URL_FILE_EXT = '.url'
PIN_FILE_EXT = '.pin'
MSG_FILE_EXT = '.msg'
URL_TOKEN_ALPHABET = \
	string.digits + string.ascii_lowercase + \
	string.digits + string.ascii_uppercase
URL_TOKEN_LENGTH = 32
PIN_ALPHABET = string.digits
PIN_LENGTH = 6
PWD_ALPHABET = string.ascii_uppercase + string.digits
PWD_LENGTH = 6
PWD_COUNT = 3
VALID_SECONDS = 60
LANGUAGES = ['en', 'ru']
MESSAGES = [
	{
		'en': 'Use keyboard to select command',
		'ru': 'Используйте клавиатуру для выбора команды'
	},
	{
		'en': 'Push button to open Website',
		'ru': 'Нажмите кнопку для перехода на Вебсайт'
	},
	{
		'en': 'Push button to confirm password for Website',
		'ru': 'Нажмите кнопку для подтверждения пароля к Вебсайту'
	}
]
KEYBOARDS = [
	[
		[
			{
				'id': '/auth_url',
				'title': {
					'en': 'Request authorization link for Website',
					'ru': 'Запросить авторизационную ссылку для Вебсайта'
				}
			}
		],
		[
			{
				'id': '/auth_pin',
				'title': {
					'en': 'Request authorization PIN for Website',
					'ru': 'Запросить авторизационный ПИН для Вебсайта'
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
LOOP_TIMEOUT = 5
COMMANDS = [
	{
		'command': '/start',
		'description': ''
	}
]
REQUEST_TIMEOUT = (3.0, 15.0)


class Plugin():
	"""
	This Plugin class describes managing process
	on identica bot communication.
	"""
	domain_url = None
	config_filename = None
	config = None
	offset = 0

	def __init__(self, domain_url: str = None) -> "Plugin":
		"""
		Inititate Plugin object with debug_mode and
		configuration data.
		"""
		self.config_filename = os.path.join(IDENTICA_PATH, IDENTICA_JSON)
		self.domain_url = domain_url
		if not self.init_config():
			raise ValueError('Initiate Error!')
		logging.debug('Identica initiated')

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
		self.config['website_marker'] = '[ %s ]' % self.config['website']
		# Initiate configuration
		self.config['bot_url']['setMyCommands'] = \
			self.config['bot_url']['setMyCommands'] % self.config['token']
		self.config['bot_url']['getUpdates'] = \
			self.config['bot_url']['getUpdates'] % self.config['token'] + \
			self.config['bot_url']['getUpdatesArguments']
		self.config['bot_url']['sendMessage'] = \
			self.config['bot_url']['sendMessage'] % self.config['token']
		self.config['bot_url']['deleteMessage'] = \
			self.config['bot_url']['deleteMessage'] % self.config['token']
		self.config['bot_url']['answerCallbackQuery'] = \
			self.config['bot_url']['answerCallbackQuery'] % self.config['token']
		if self.domain_url is not None:
			self.config['auth_url'] = \
				'/'.join([self.domain_url] + self.config['auth_url'].split('/')[-2:])
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
		logging.debug('Identica configuration initiated')
		return True

	def run(self) -> None:
		"""
		Run infinite loop to manage communication through files in folder.
		"""
		try:
			result = True
			logging.debug('Identica start main loop')
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
					# List message files to send messages (and document/photo)
					mtime = time.time()
					for filename in os.listdir(IDENTICA_PATH):
						if filename.endswith(MSG_FILE_EXT):
							with open(os.path.join(IDENTICA_PATH, filename), 'r') as file:
								msg_data = json.loads(file.read())
								response = requests.get(
									self.config['bot_url']['sendMessage'],
									json=msg_data, timeout=REQUEST_TIMEOUT
								)
								if not response.json()['ok']:
									logging.error(response.json())
									result = False
							os.remove(os.path.join(IDENTICA_PATH, filename))
						elif (filename.endswith(URL_FILE_EXT) or \
								filename.endswith(PIN_FILE_EXT)):
							filepath = os.path.join(IDENTICA_PATH, filename)
							if mtime - os.path.getmtime(filepath) > VALID_SECONDS:
								os.remove(os.path.join(IDENTICA_PATH, filename))
				except KeyboardInterrupt:
					break
				except:
					logging.error('Error while running', exc_info=1)
				time.sleep(LOOP_TIMEOUT) # Prevent overhead
		except KeyboardInterrupt:
			pass
		logging.debug('Identica stop main loop')

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
		elif '\n' in message['text']:
			pseudo_command_title, marker = message['text'].split('\n')
			if marker not in [
						'[ %s ]' % self.config['name'],
						self.config['website_marker']
					]:
				return True
			pseudo_command = PSEUDO_COMMANDS.get(pseudo_command_title)
			if pseudo_command == '/auth_url':
				url_token = ''.join(
					secrets.choice(URL_TOKEN_ALPHABET) \
					for _ in range(URL_TOKEN_LENGTH)
				)
				url_filename = os.path.join(
					IDENTICA_PATH, url_token + URL_FILE_EXT)
				with open(url_filename, 'w') as file:
					file.write(json.dumps({
						'from': message['from'],
						'valid': (
							datetime.utcnow() + timedelta(seconds=VALID_SECONDS)
						).timestamp()
					}))
				response = self.send_url(
					message['chat']['id'], MESSAGES[1][language],
					self.config['auth_url'] % url_token
				)
			elif pseudo_command == '/auth_pin':
				pin = ''.join(
					secrets.choice(PIN_ALPHABET) \
					for _ in range(PIN_LENGTH)
				)
				passwords = [
					''.join(
						secrets.choice(PWD_ALPHABET) \
						for _ in range(PWD_LENGTH)
					) for _ in range(PWD_COUNT)
				]
				pin_filename = os.path.join(
					IDENTICA_PATH, pin + PIN_FILE_EXT)
				with open(pin_filename, 'w') as file:
					file.write(json.dumps({
						'from': message['from'],
						'password': secrets.choice(passwords),
						'confirmed': False,
						'valid': (
							datetime.utcnow() + timedelta(seconds=VALID_SECONDS)
						).timestamp()
					}))
				response = self.send_pin(
					message['chat']['id'], MESSAGES[2][language],
					pin, passwords
				)
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
		if callback['data'].endswith(self.config['website_marker']):
			pin_password, _ = callback['data'].split('\n')
			pin, password = pin_password.split(' ')
			pin_filename = os.path.join(
				IDENTICA_PATH, pin + PIN_FILE_EXT)
			confirmation_message = 'Fail'
			if os.path.isfile(pin_filename):
				with open(pin_filename, 'r') as file:
					pin_data = json.loads(file.read())
				if pin_data['password'] == password and \
						pin_data['valid'] > datetime.utcnow().timestamp():
					pin_data['confirmed'] = True
					confirmation_message = 'Success'
					with open(pin_filename, 'w') as file:
						file.write(json.dumps(pin_data))
				else:
					os.remove(pin_filename)
			response = requests.get(
				self.config['bot_url']['answerCallbackQuery'],
				json={
					'callback_query_id': callback['id'],
					'text': confirmation_message
				},
				timeout=REQUEST_TIMEOUT
			)
			response = requests.get(
				self.config['bot_url']['sendMessage'],
				json={
					'chat_id': callback['message']['chat']['id'],
					'text': MESSAGES[0][language],
				},
				timeout=REQUEST_TIMEOUT
			)
			return True
		else: # Ignore other callbacks
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
		marker = self.config['website_marker'] \
			if use_website else '[ %s ]' % self.config['name']
		return requests.get(
			self.config['bot_url']['sendMessage'],
			json={
				'chat_id': chat_id,
				'text': MESSAGES[0][language],
				'reply_markup':{
					'keyboard': [
						[
							{
								'text': '%s\n%s' % (button[0]['title'][language], marker)
							}
						] for button in keyboard
					]
				}
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

	def send_url(self, chat_id: str, message: str,
							 url: str) -> dict:
		"""
		Send website link button to user within chat message
		and return response dictionary.
		"""
		return requests.get(
			self.config['bot_url']['sendMessage'],
			json={
				'chat_id': chat_id,
				'text': message,
				'reply_markup':{
					'inline_keyboard': [
						[
							{ 'text': self.config['website_marker'], 'url': url }
						]
					]
				}
			},
			timeout=REQUEST_TIMEOUT
		).json()

	def send_pin(self, chat_id: str, message: str,
							 pin: str, passwords: list) -> dict:
		"""
		Send pin to user within chat message
		and return response dictionary.
		"""
		requests.get(
			self.config['bot_url']['sendMessage'],
			json={
				'chat_id': chat_id,
				'text': 'PIN: <code>%s</code>' % pin,
				'parse_mode': 'HTML'
			},
			timeout=REQUEST_TIMEOUT
		)
		inline_keyboard = [
			[
				{
					'text': password,
					'callback_data': '%s %s\n%s' % \
						(pin, password, self.config['website_marker'])
				}
			] for password in passwords
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
	def verify_url(url_token: str) -> dict:
		"""
		Return dictionary with user data or return null.
		"""
		url_filename = os.path.join(
			IDENTICA_PATH, url_token + URL_FILE_EXT)
		if not os.path.isfile(url_filename):
			logging.warning('URL file not found: %s' % url_filename)
			return
		with open(url_filename, 'r') as file:
			url_data = json.loads(file.read())
		if url_data['valid'] < datetime.utcnow().timestamp():
			logging.warning('URL invalid: %s' % pin_filename)
			return
		os.remove(url_filename)
		return { 'from': url_data['from'] }

	@staticmethod
	def get_password(pin: str) -> str:
		"""
		Return password for pin or return null.
		"""
		pin_filename = os.path.join(
			IDENTICA_PATH, pin + PIN_FILE_EXT)
		if not os.path.isfile(pin_filename):
			logging.warning('PIN file not found: %s' % pin_filename)
			return
		with open(pin_filename, 'r') as file:
			pin_data = json.loads(file.read())
		if pin_data['valid'] < datetime.utcnow().timestamp():
			logging.warning('PIN invalid: %s' % pin_filename)
			return
		return pin_data['password']

	@staticmethod
	def verify_pin(pin: str) -> dict:
		"""
		Return dictionary with user data or return null.
		"""
		pin_filename = os.path.join(
			IDENTICA_PATH, pin + PIN_FILE_EXT)
		if not os.path.isfile(pin_filename):
			logging.warning('PIN file not found: %s' % pin_filename)
			return
		with open(pin_filename, 'r') as file:
			pin_data = json.loads(file.read())
		if pin_data['valid'] < datetime.utcnow().timestamp():
			logging.warning('PIN invalid: %s' % pin_filename)
			os.remove(pin_filename)
			return
		if not pin_data['confirmed']:
			logging.warning('PIN not confirmed: %s' % pin_filename)
			return {}
		os.remove(pin_filename)
		return { 'from': pin_data['from'] }

	@staticmethod
	def notify_user(chat_id: str, text: str) -> None:
		"""
		Send notification message.
		"""
		msg_filename = os.path.join(
			IDENTICA_PATH,
			''.join(
				secrets.choice(PWD_ALPHABET) \
				for _ in range(PWD_LENGTH)
			) + MSG_FILE_EXT
		)
		with open(msg_filename, 'w', encoding='utf8') as file:
			file.write(
				json.dumps(
					{ 'chat_id': chat_id, 'text': text },
					ensure_ascii=False
				)
			)
