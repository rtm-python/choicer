# -*- coding: utf-8 -*-

"""
Service module to handle Option form.
"""

# Standard libraries import
import logging

# Application modules import
from blueprints.__form__ import InputForm
from models.option_store import OptionStore
from models.entity.option import Option

# Additional libraries import
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField


class OptionForm(InputForm):
	"""
	This is a OptionForm class to retrieve form data.
	"""
	value = StringField('Value')

	def __init__(self, uid: str = None) -> "OptionForm":
		"""
		Initiate object with values fron request.
		"""
		super(OptionForm, self).__init__('optionForm')
		if request.method == 'GET':
			if uid is not None:
				option = OptionStore().read(uid)
				self.value.data = option.value
		elif request.method == 'POST':
			self.form_valid = True

	def create(self) -> Option:
		"""
		Create option entity.
		"""
		return OptionStore().create(value=self.value.data)

	def update(self, uid: str) -> Option:
		"""
		Update option entity.
		"""
		return OptionStore().update(uid=uid, value=self.value.data)
