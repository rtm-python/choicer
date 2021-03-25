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
from blueprints.__form__ import ReordererFormAbstract
from blueprints.__list__ import Pagination
from models.poll_store import PollStore
from models.file_store import FileStore
from models.entity.poll import Poll
from models.entity.file import File

# Additional libraries import
from flask import url_for
from flask import redirect
from flask import request
from flask import url_for
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField


class PollFilter(InputForm):
	"""
	This is a PollFilter class to retrieve form data.
	"""
	title = StringField('Title')
	description = StringField('Description')
	reset = SubmitField('Reset')

	def __init__(self) -> "PollFilter":
		"""
		Initiate object with values from request.
		"""
		super(PollFilter, self).__init__('pollFilter')
		if request.method == 'GET':
			self.title.data = blueprints.get_value(
				self.title.label.text, str, None)
			self.description.data = blueprints.get_value(
				self.description.label.text, str, None)
		elif request.method == 'POST':
			blueprints.set_value(
				self.title.label.text, self.title.data)
			blueprints.set_value(
				self.description.label.text, self.description.data)
			self.form_valid = True

	def reset_fields(self) -> None:
		"""
		Reset all fields values to None.
		"""
		for field in self:
			if field.name != 'csrf_token' and field.name != 'form_name':
				field.data = None
				blueprints.set_value(field.label.text, field.data)


class PollList():
	"""
	This is a PollList class to handle poll list.
	"""
	pagination = None

	def __init__(self, endpoint: str) -> "PollList":
		"""
		Initiate object.
		"""
		self.pagination = Pagination('pollList', endpoint)

	def read_list(self, filter: PollFilter) -> (Pagination, [Poll]):
		"""
		Return pagination and list of poll entities filtered by filter.
		"""
		poll_store = PollStore()
		poll_count, poll_list = poll_store.read_list(
			(self.pagination.page_index - 1) * self.pagination.per_page,
			self.pagination.per_page, filter.title.data, filter.description.data
		)
		if not self.pagination.validate(poll_count):
			poll_count, poll_list = poll_store.read_list(
				(self.pagination.page_index - 1) * self.pagination.per_page,
				self.pagination.per_page, filter.title.data, filter.description.data
			)
		return (self.pagination, poll_list)

	@staticmethod
	def delete(uid: str) -> Poll:
		"""
		Delete and return poll entity by uid.
		"""
		return PollStore().delete(uid)

	@staticmethod
	def read(uid: str) -> (Poll, File):
		"""
		Return poll and linked file entity by uid.
		"""
		poll = PollStore().read(uid)
		file = FileStore().get(poll.image_id)
		return (poll, file)
