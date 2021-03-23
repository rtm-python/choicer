# -*- coding: utf-8 -*-

"""
Utility module to handle forms.
"""

# Standard libraries import
import logging
import json

# Application modules import
import blueprints
from blueprints.__file__ import temporary_file
from blueprints.__file__ import remove_file
from blueprints.__file__ import store_file
from models.file_store import FileStore
from config import TEMPORARY_PATH
from config import DATABASE_FILES_PATH

# Additional libraries import
from flask import request
from flask import url_for
from flask import send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField


class InputForm(FlaskForm):
	"""
	This is a InputForm class to retrieve form data.
	"""
	__abstract__ = True
	form_name = None
	form_valid = None
	submit = SubmitField('Submit')

	def __init__(self, form_name: str) -> "InputForm":
		"""
		Initiate object with values from request.
		"""
		super(InputForm, self).__init__()
		self.form_name = form_name
		self.make_prefixed()
		for field in self:
			if field.name != 'csrf_token' and field.name != 'form_name' and \
					not field.name.startswith('__'):
				data = request.form.get(field.label.text)
				field.data = data if data is not None and len(data) > 0 else None

	def make_prefixed(self) -> None:
		"""
		Add prefix with formname to each field label.
		"""
		for field in self:
			if field.name != 'csrf_token' and field.name != 'form_name' and \
					not field.name.startswith('__'):
				field.label.text = self.form_name + field.label.text

	def __str__(self) -> str:
		"""
		String representation of the form.
		"""
		return 'InputForm(%s): ' % self.form_name + \
			', '.join([
				'%s (%s) = %s' % (
					field.name, field.label.text, field.data
				) for field in self
			])


class ReordererFormAbstract(InputForm):
	"""
	This is a ReordererForm class to retrieve form data.
	"""
	__abstract__ = True
	data = StringField('Data')

	def __init__(self) -> "ReordererFormAbstract":
		"""
		Initiate object with values from request.
		"""
		super(ReordererFormAbstract, self).__init__('reordererForm')
		if request.method == 'GET':
			self.data.data = None
		elif request.method == 'POST':
			if self.data.data is not None:
				self.form_valid = True


class FileForm(FlaskForm):
	"""
	This is a FileForm class to retrieve form data.
	"""

	def __init__(self, uid: str = None) -> "FileForm":
		"""
		Initiate object with values fron request.
		"""
		if request.method == 'POST':
			blueprints.csrf.protect()

	def upload(self) -> str:
		"""
		Upload file and return info data for uploaded file.
		"""
		file = request.files.get('file')
		if file is not None:
			fileinfo = temporary_file(file)
		if fileinfo is not None:
			return {
				'status': 'ok',
				'fileinfo': fileinfo
			}, 200
		return blueprints.__('Upload error'), 500

	@staticmethod
	def download(uid: str):
		"""
		Return downloadable file object.
		"""
		file = FileStore().read(uid)
		if file is not None:
			return send_from_directory(file.path, file.name)
		else:
			abort(404)


class InputWithFilesForm(InputForm):
	"""
	This is a InputWithFilesForm class to retrieve form data.
	"""
	__abstract__ = True
	files = StringField('Files')

	def init_files(self, files: list) -> None:
		"""
		Initiate files field with files data.
		"""
		data = {}
		for file in files:
			data['server/%s' %file.title] = {
				'uid': file.uid,
				'url': url_for('root.download', uid=file.uid),
				'uploaded': False,
				'removed': False,
				'name': file.name,
				'size': file.size
			}
		self.files.data = json.dumps(data)

	def save_files(self, limit: int) -> list:
		"""
		Synchronize with moving temporary files
		or removing stored files (if limit less zero then unlimited).
		"""
		result = []
		for filename, filedata in json.loads(self.files.data).items():
			if filedata['removed'] or limit == 0:
				# file should be removed
				remove_file(filedata)
			elif limit != 0:
				if filedata['uploaded']:
					# file should be stored
					result += [store_file(filedata, DATABASE_FILES_PATH)]
				else:
					# file should be present on server
					result += [FileStore().read(filedata['uid'])]
				limit -= 1
		return result
