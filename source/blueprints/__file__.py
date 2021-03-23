# -*- coding: utf-8 -*-

"""
Utility module to handle files.
"""

# Standard libraries import
import logging
import json
import uuid
import os

# Application modules import
from config import CONFIG
from config import TEMPORARY_PATH
from models.entity.file import File
from models.file_store import FileStore


def make_dirs(filepath: str) -> None:
	"""
	Make subfolders for filepath.
	"""
	if not os.path.exists(filepath):
		try:
			os.makedirs(filepath)
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				raise


def temporary_file(file) -> dict:
	"""
	Store temporary file and return fileinfo.
	"""
	if file.content_type not in CONFIG['allowed_types']:
		return # Not allowed content type
	# Generate subfolder structure
	sequence = ''.join(str(uuid.uuid4()).split('-'))
	subfolder = os.path.join(
		*[
			sequence[index: index + 2] \
				for index in range(0, len(sequence), 2)
		]
	)
	make_dirs(os.path.join(TEMPORARY_PATH, subfolder))
	# Generate fileinfo and return filedata
	name = str(uuid.uuid4())
	title = file.filename
	type = file.content_type
	file.save(os.path.join(TEMPORARY_PATH, subfolder, name))
	size = os.stat(os.path.join(TEMPORARY_PATH, subfolder, name)).st_size
	with open(os.path.join(TEMPORARY_PATH, name), 'w') as file:
		file.write(
			json.dumps(
				{
					'name': name,
					'subfolder': subfolder,
					'size': size,
					'title': title,
					'type': type
				}
			)
		)
	return {
		'uid': None,
		'url': None,
		'uploaded': True,
		'removed': False,
		'name': name,
		'size': size
	}


def remove_file(filedata: dict) -> None:
	"""
	Remove file according to filedata (temporary file or stored on server).
	"""
	if filedata['uploaded']:
		# uploaded file should be removed
		infopath = os.path.join(TEMPORARY_PATH, filedata['name'])
		with open(infopath, 'r') as file:
			fileinfo = json.loads(file.read())
		os.remove(infopath)
		os.remove(os.path.join(
			TEMPORARY_PATH, fileinfo['subfolder'], fileinfo['name']))
	else:
		# file on server should be removed
		file = FileStore().delete(filedata['uid'])
		os.remove(os.path.join(file.path, file.name))


def store_file(filedata: dict, target: str) -> File:
	"""
	Move temporary file to target with all subfolders,
	create and return File object.
	"""
	# Read data from fileinfo
	with open(os.path.join(TEMPORARY_PATH, filedata['name']), 'r') as file:
		fileinfo = json.loads(file.read())
	temporary_path = os.path.join(TEMPORARY_PATH, fileinfo['subfolder'])
	target_path = os.path.join(target, fileinfo['subfolder'])
	# Move file with subfolder structure, create and return File object
	make_dirs(target_path)
	os.rename(
		os.path.join(temporary_path, fileinfo['name']),
		os.path.join(target_path, fileinfo['name'])
	)
	os.remove(os.path.join(TEMPORARY_PATH, fileinfo['name']))
	return FileStore().create(
		title=fileinfo['title'], name=fileinfo['name'],
		type=fileinfo['type'], path=target_path, size=fileinfo['size']
	)
