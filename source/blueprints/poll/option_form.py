# -*- coding: utf-8 -*-

"""
Service module to handle Option form.
"""

# Standard libraries import
import logging
import json
import os

# Application modules import
from blueprints.__form__ import InputWithFilesForm
from blueprints.__file__ import store_file
from config import TEMPORARY_PATH
from config import DATABASE_FILES_PATH
from models.poll_store import PollStore
from models.option_store import OptionStore
from models.file_store import FileStore
from models.entity.option import Option

# Additional libraries import
from flask import request
from flask import abort
from flask import url_for
from wtforms import StringField


class OptionForm(InputWithFilesForm):
	"""
	This is a OptionForm class to retrieve form data.
	"""
	title = StringField('Title')
	description = StringField('Description')

	def __init__(self, uid: str = None) -> "OptionForm":
		"""
		Initiate object with values fron request.
		"""
		super(OptionForm, self).__init__('optionForm')
		if request.method == 'GET':
			if uid is not None:
				option = OptionStore().read(uid)
				if option is None:
					abort(404)
				self.title.data = option.title
				self.description.data = option.description
				file = FileStore().get(option.image_id)
				if file is not None:
					self.init_files([file])
		elif request.method == 'POST':
			self.form_valid = True
			if self.title.data is None:
				self.title.errors = ['Value required']
				self.form_valid = False

	def create(self, poll_uid: str) -> Option:
		"""
		Create option entity.
		"""
		files = self.save_files(1)
		file_id = files[0].id if files else None
		return OptionStore().create(
			poll_id=PollStore().read(poll_uid).id,
			title=self.title.data, description=self.description.data,
			image_id=file_id
		)

	def update(self, uid: str) -> Option:
		"""
		Update option entity.
		"""
		files = self.save_files(1)
		file_id = files[0].id if files else None
		return OptionStore().update(
			uid=uid, title=self.title.data, description=self.description.data,
			image_id=file_id
		)
