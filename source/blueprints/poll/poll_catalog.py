# -*- coding: utf-8 -*-

"""
Service module to handle Poll catalog.
"""

# Standard libraries import
import logging
import os
import json
from datetime import datetime
from datetime import timedelta

# Application modules import
import blueprints
from blueprints.__form__ import InputForm
from blueprints.__form__ import ReordererFormAbstract
from blueprints.__list__ import Pagination
from plugins.choicer import Plugin as ChoicerPlugin
from blueprints.poll.option_catalog import OptionList
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

	@staticmethod
	def start(uid: str) -> Poll:
		"""
		Start poll by uid.
		"""
		poll, file = PollList.read(uid)
		poll_data = {
			'title': poll.title,
			'description': poll.description,
			'image': {
				'filepath': os.path.join(file.path, file.name) \
					if file else None,
				'uid': file.uid if file else None,
			},
			'options': []
		}
		vote_data = None \
			if poll.vote_data is None else json.loads(poll.vote_data)
		for option, file in OptionList.options(uid):
			poll_data['options'] += [
				{
					'title': option.title,
					'description': option.description,
					'image': {
						'filepath': os.path.join(file.path, file.name) \
							if file else None,
						'uid': file.uid if file else None,
					}
				}
			]
		free_uid = ChoicerPlugin.free_poll()
		while free_uid is not None:
			poll_count, poll_list =	PollStore().read_list(
				None, None, None, None, free_uid)
			if poll_count > 0:
				PollList.stop(poll_list[0][0].uid)
			free_uid = ChoicerPlugin.free_poll()
		data_uid = ChoicerPlugin.play_poll(poll_data, vote_data)
		return PollStore().set_data_uid(uid=uid, data_uid=data_uid)

	@staticmethod
	def stop(uid: str) -> Poll:
		"""
		Stop poll by uid.
		"""
		poll = PollStore().read(uid)
		if poll.data_uid is not None:
			poll_data = ChoicerPlugin.stop_poll(poll.data_uid)
			if poll_data is not None:
				vote_data = {
					'results': poll_data['results'],
					'voters': poll_data['voters']
				}
				poll = PollStore().set_vote_data(
					uid=uid, vote_data=json.dumps(vote_data))
			poll = PollStore().set_data_uid(uid=uid, data_uid=None)
		return poll
