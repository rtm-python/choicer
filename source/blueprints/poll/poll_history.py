# -*- coding: utf-8 -*-

"""
Service module to handle Poll catalog.
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
from models.poll_history_store import PollHistoryStore
from models.entity.poll_history import PollHistory

# Additional libraries import
from flask import url_for
from flask import redirect
from flask import request
from flask import url_for
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField


class PollHistoryFilter(InputForm):
	"""
	This is a PollHistoryFilter class to retrieve form data.
	"""
	username = StringField('Username')
	value = StringField('Value')
	event = StringField('Event')
	reset = SubmitField('Reset')

	def __init__(self) -> "PollHistoryFilter":
		"""
		Initiate object with values from request.
		"""
		super(PollHistoryFilter, self).__init__('pollHistoryFilter')
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


class PollHistoryList():
	"""
	This is a PollHistoryList class to handle poll list.
	"""
	pagination = None

	def __init__(self, endpoint: str) -> "PollHistoryList":
		"""
		Initiate object.
		"""
		self.pagination = Pagination('pollHistoryList', endpoint)

	def read_list(self, filter: PollHistoryFilter
							 ) -> (Pagination, [PollHistory]):
		"""
		Return pagination and list of poll entities filtered by filter.
		"""
		poll_history_store = PollHistoryStore()
		poll_history_count, poll_history_list = \
			poll_history_store.read_list(
				(self.pagination.page_index - 1) * self.pagination.per_page,
				self.pagination.per_page, filter.username.data,
				filter.value.data, filter.event.data
			)
		if not self.pagination.validate(poll_history_count):
			poll_history_count, poll_history_list = \
				poll_history_store.read_list(
					(self.pagination.page_index - 1) * self.pagination.per_page,
					self.pagination.per_page, filter.username.data,
					filter.value.data, filter.event.data
				)
		return (self.pagination, poll_history_list)

	@staticmethod
	def create(user_id: int, poll_id: int, event: str) -> None:
		"""
		Create Poll history in database.
		"""
		PollHistoryStore().create(user_id, poll_id, event)
