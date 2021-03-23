# -*- coding: utf-8 -*-

"""
Service module to handle Option catalog.
"""

# Standard libraries import
import logging
import json
from datetime import datetime
from datetime import timedelta

# Application modules import
import blueprints
from blueprints.__form__ import InputForm
from blueprints.__form__ import ReordererFormAbstract
from blueprints.__list__ import Pagination
from models.option_store import OptionStore
from models.entity.option import Option

# Additional libraries import
from flask import url_for
from flask import redirect
from flask import request
from flask import url_for
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField


class OptionFilter(InputForm):
	"""
	This is a OptionFilter class to retrieve form data.
	"""
	value = StringField('Value')
	reset = SubmitField('Reset')

	def __init__(self) -> "OptionFilter":
		"""
		Initiate object with values from request.
		"""
		super(OptionFilter, self).__init__('optionFilter')
		if request.method == 'GET':
			self.value.data = blueprints.get_value(self.value.label.text, str, None)
		elif request.method == 'POST':
			blueprints.set_value(self.value.label.text, self.value.data)
			self.form_valid = True

	def reset_fields(self) -> None:
		"""
		Reset all fields values to None.
		"""
		for field in self:
			if field.name != 'csrf_token' and field.name != 'form_name':
				field.data = None
				blueprints.set_value(field.label.text, field.data)


class OptionList():
	"""
	This is a OptionList class to handle option list.
	"""
	pagination = None

	def __init__(self, endpoint: str) -> "OptionList":
		"""
		Initiate object.
		"""
		self.pagination = Pagination('optionList', endpoint)

	def read_list(self, filter: OptionFilter) -> (Pagination, [Option]):
		"""
		Return pagination and list of option entities filtered by filter.
		"""
		option_store = OptionStore()
		option_count, option_list = option_store.read_list(
			(self.pagination.page_index - 1) * self.pagination.per_page,
			self.pagination.per_page, filter.value.data
		)
		if not self.pagination.validate(option_count):
			option_count, option_list = option_store.read_list(
				(self.pagination.page_index - 1) * self.pagination.per_page,
				self.pagination.per_page, filter.value.data
			)
		return (self.pagination, option_list)

	@staticmethod
	def delete(uid: str) -> Option:
		"""
		Delete option entity by uid.
		"""
		return OptionStore().delete(uid)


class ReordererForm(ReordererFormAbstract):
	"""
	This is a ReordererForm class.
	"""

	def reorder(self) -> None:
		"""
		Reorder elements.
		"""
		option_store = OptionStore()
		order_utc = datetime.utcnow()
		for uid in json.loads(self.data.data)['uidList']:
			option_store.reorder(uid, order_utc)
			order_utc = order_utc - timedelta(microseconds=1)
