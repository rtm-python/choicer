# -*- coding: utf-8 -*-

"""
Store module for file entity.
"""

# Stabdard libraries import
from datetime import datetime

# Application modules import
from models import database
from models import Store
from models.entity.file import File


class FileStore(Store):
	"""
	This is a file class.
	"""

	def __init__(self) -> "FileStore":
		"""
		Initiate FileStore object.
		"""
		super(FileStore, self).__init__(File)

	def create(self, title: str,
						 name: str, type: str, path: str, size: int) -> File:
		"""
		Create and return file.
		"""
		return super().create(
			title=title, name=name, type=type, path=path, size=size
		)

	def rename(self, uid: str, title: str) -> File:
		"""
		Update and return file.
		"""
		return super().update(
			uid=uid, title=title
		)

	def read_list(self, offset: int, limit: int,
							  name: str, type: str) -> list:
		"""
		Return total number and list of file by arguments.
		"""
		query = database.session.query(
			File
		).filter(
			True if name is None else \
				File.name.contains(name),
			True if type is None else \
				File.type.contains(type),
			File.deleted_utc == None
		).order_by(
			File.modified_utc.desc()
		)
		return (
			self.count(query),
			query.limit(limit).offset(offset).all()
		)
