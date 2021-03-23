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
from blueprints.__list__ import Pagination
from models.option_history_store import OptionHistoryStore
from models.entity.option_history import OptionHistory

# Additional libraries import
from flask import url_for
from flask import redirect
from flask import request
from flask import url_for
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField


class OptionHistoryFilter(InputForm):
	"""
	This is a OptionHistoryFilter class to retrieve form data.
	"""
	username = StringField('Username')
	value = StringField('Value')
	event = StringField('Event')
	reset = SubmitField('Reset')

	def __init__(self) -> "OptionHistoryFilter":
		"""
		Initiate object with values from request.
		"""
		super(OptionHistoryFilter, self).__init__('optionHistoryFilter')
		if request.method == 'GET':
			self.username.data = blueprints.get_value(self.username.label.text, str, None)
			self.value.data = blueprints.get_value(self.value.label.text, str, None)
			self.event.data = blueprints.get_value(self.event.label.text, str, None)
		elif request.method == 'POST':
			blueprints.set_value(self.username.label.text, self.username.data)
			blueprints.set_value(self.value.label.text, self.value.data)
			blueprints.set_value(self.event.label.text, self.event.data)
			self.form_valid = True

	def reset_fields(self) -> None:
		"""
		Reset all fields values to None.
		"""
		for field in self:
			if field.name != 'csrf_token' and field.name != 'form_name' and \
					not field.name.startswith('__'):
				field.data = None
				blueprints.set_value(field.label.text, field.data)


class OptionHistoryList():
	"""
	This is a OptionHistoryList class to handle option list.
	"""
	pagination = None

	def __init__(self, endpoint: str) -> "OptionHistoryList":
		"""
		Initiate object.
		"""
		self.pagination = Pagination('optionHistoryList', endpoint)

	def read_list(self, filter: OptionHistoryFilter
							 ) -> (Pagination, [OptionHistory]):
		"""
		Return pagination and list of option entities filtered by filter.
		"""
		option_history_store = OptionHistoryStore()
		option_history_count, option_history_list = \
			option_history_store.read_list(
				(self.pagination.page_index - 1) * self.pagination.per_page,
				self.pagination.per_page, filter.username.data,
				filter.value.data, filter.event.data
			)
		if not self.pagination.validate(option_history_count):
			option_history_count, option_history_list = \
				option_history_store.read_list(
					(self.pagination.page_index - 1) * self.pagination.per_page,
					self.pagination.per_page, filter.username.data,
					filter.value.data, filter.event.data
				)
		return (self.pagination, option_history_list)

	@staticmethod
	def create(user_id: int, option_id: int, event: str) -> None:
		"""
		Create Option history in database.
		"""
		OptionHistoryStore().create(user_id, option_id, event)
