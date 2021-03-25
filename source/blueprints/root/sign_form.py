# -*- coding: utf-8 -*-

"""
Blueprint module to handle home routes.
"""

# Standard libraries import
import logging

# Application modules import
import blueprints
from blueprints.root import blueprint
from blueprints.__init__ import SignedInUser
from blueprints.__form__ import InputForm
from plugins.identica import Plugin as IdenticaPlugin
from plugins.admin import permission_required
from models.user_store import UserStore
from models.entity.user import User

# Additional libraries import
from flask import url_for
from flask_login import login_user
from flask_login import current_user
from flask import redirect
from flask import request
from flask import url_for
from wtforms import StringField
from wtforms import SubmitField


class SignInForm(InputForm):
	"""
	This is a SignInForm class to retrieve form data.
	"""
	has_touch_screen = StringField('HasTouchScreen')
	url_token = StringField('UrlToken')
	pin = StringField('Pin')
	password = StringField('Password')

	def __init__(self, url_token: str) -> "SignInForm":
		"""
		Initiate object with values from request.
		"""
		super(SignInForm, self).__init__('signInForm')
		if url_token is not None:
			self.url_token.data = url_token

	def authenticate(self) -> bool:
		"""
		Authenticate user by form data and return True on success.
		"""
		if self.url_token.data is not None:
			verify_data = IdenticaPlugin.verify_url(self.url_token.data)
			if verify_data is not None and verify_data.get('from'):
				user = UserStore().read_or_create_user(
					verify_data['from']['id'],
					verify_data['from'].get('first_name'),
					verify_data['from'].get('last_name'),
					verify_data['from'].get('username')
				)
				login_user(SignedInUser(user), remember=True)
				logging.debug('Sign in as user %s (%s)' % \
					(' '.join([user.first_name, user.last_name]), user.from_id))
				blueprints.set_value(
					'mobile', self.has_touch_screen.data == 'true')
			return redirect(url_for('root.get_home'))
		elif self.pin.data is not None:
			if self.password.data is None:
				password = IdenticaPlugin.get_password(self.pin.data)
				if password is None:
					return redirect(url_for('root.get_home'))
				self.password.data = password
			else:
				verify_data = IdenticaPlugin.verify_pin(self.pin.data)
				if verify_data is None:
					return { 'redirect': url_for('root.get_home') }
				elif verify_data.get('from'):
					user = UserStore().read_or_create_user(
						verify_data['from']['id'],
						verify_data['from'].get('first_name'),
						verify_data['from'].get('last_name'),
						verify_data['from'].get('username')
					)
					login_user(SignedInUser(user), remember=True)
					logging.debug('Sign in as user %s (%s)' % \
						(' '.join([user.first_name, user.last_name]), user.from_id))
					blueprints.set_value(
						'mobile', self.has_touch_screen.data == 'true')
					return { 'redirect': url_for('root.get_home') }
				return { 'wait': True }
		return # Return None to render template
