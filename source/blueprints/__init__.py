# -*- coding: utf-8 -*-

"""
Initial blueprints module to define blueprints.
"""

# Standard libraries import
import secrets
import importlib

# Application modules import
from config import CONFIG
from config import LOCALE
from config import STATIC_PATH
from config import TEMPLATE_PATH

# Additional libraries import
from flask import Flask
from flask import session
from flask import request
from flask_paranoid import Paranoid
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import AnonymousUserMixin
from flask_wtf.csrf import CSRFProtect

# Initiate Flask object
application = Flask(
	CONFIG['name'], static_url_path='',
	static_folder=STATIC_PATH, template_folder=TEMPLATE_PATH
)
application.config['SECRET_KEY'] = CONFIG['secret_key']
application.config['MAX_CONTENT_LENGTH'] = CONFIG['max_content_length']


class SignedInUser(UserMixin):
	"""
	This is a SignedInUser class to handle data of authenticated user.
	"""
	user = None

	def __init__(self, user):
		super().__init__()
		self.user = user

	def get_id(self):
		"""
		Return uid for linked to SignedInUser object User entity.
		"""
		if self.user is not None:
			return self.user.uid

	def get_token(self):
		"""
		Return None for SignedInUser object (no anonymous token).
		"""
		return None


class AnonymousUser(AnonymousUserMixin):
	"""
	This is a AnonymousUser class to handle data of anonymous user.
	"""

	def get_id(self):
		"""
		Return None for AnonymousUser object (no user uid).
		"""
		return None

	def get_token(self):
		"""
		Return anonymous token for anonymous user.
		"""
		anonymous_token = session.get('anonymous_token')
		if anonymous_token is None:
			anonymous_token = secrets.token_hex(256)
			session['anonymous_token'] = anonymous_token
		return anonymous_token


# Initiate LoginManager object
login_manager = LoginManager(application)
login_manager.anonymous_user = AnonymousUser
login_manager.session_protection = 'strong'

# Import and register blueprint modules
# (prevent circular imports)
for module_name, url_prefix in [
			('root', '/'),
			('poll', '/poll/'),
			('option', '/option/')
		]:
	module = importlib.import_module('blueprints.%s' % module_name)
	application.register_blueprint(module.blueprint, url_prefix=url_prefix)

# Initiate Paranoid object
paranoid = Paranoid(application)
paranoid.redirect_view = 'root.get_home'

# Initiate CSRF object
csrf = CSRFProtect(application)

# Import User and UserStore from models
from models.entity.user import User
from models.user_store import UserStore


@login_manager.user_loader
def load_user(user_id):
	"""
	Return SignedInUser object linked to User entity by uid.
	"""
	return SignedInUser(UserStore().read(user_id))


@application.before_request
def make_session_permanent():
	"""
	Make all sessions permanent.
	"""
	session.permanent = True


@application.before_request
def set_session_language():
	"""
	Set session language from client request.
	"""
#	session['language'] = 'ru'
	session['language'] = request.accept_languages.best_match(
		LOCALE['__']['supported_languages']
	)


@application.context_processor
def get_dictionary():
	"""
	Return dictionary from text string.
	"""
	def _dict(text: str) -> dict:
		return __dict(text)
	return dict(__dict=__dict)


def __dict(text: str) -> dict:
	"""
	Return dictionary from text string.
	"""
	return json.loads(text)


@application.context_processor
def get_config():
	"""
	Return configuration data by key.
	"""
	def _config(key: str) -> object:
		return __config(key)
	return dict(__config=__config)


def __config(key: str) -> object:
	"""
	Return configuration data by key.
	"""
	return CONFIG.get(key)


@application.context_processor
def get_localized():
	"""
	Return localized text string.
	"""
	def _(key: str) -> str:
		return __(key)
	return dict(__=__)


def __(key: str) -> str:
	"""
	Return matching by key localized text string.
	"""
	value = LOCALE.get(key)
	if value:
		localized = value.get(session['language'])
		if localized:
			return localized
	return key


def get_value(name: str, value_type, default) -> object:
	"""
	Return cast to type value from request or session.
	"""
	for args in [request.args, session.get('args') or {}]:
		value = args.get(name)
		if value is not None:
			try:
				if value_type is int:
					return int(value)
				elif value_type is str:
					return str(value)
				elif value_type is bool:
					return value == 'true' or value == 'True' or \
						value == 'on' or value is True
			except:
				logging.warning('Value casting error!')
	return default


def set_value(name: str, value: int) -> None:
	"""
	Set name, value pair to session args dictionary.
	"""
	args = session.get('args') or {}
	args[name] = value
	session['args'] = args
