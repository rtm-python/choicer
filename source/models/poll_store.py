# -*- coding: utf-8 -*-

'''
Store module for Poll entity.
'''

# Standard libraries import
from datetime import datetime

# Application modules import
from models import database
from models import Store
from models.entity.poll import Poll
from models.entity.file import File

# Additional libraries import
from sqlalchemy import and_


class PollStore(Store):
	"""
	This is a PollStore class.
	"""

	def __init__(self) -> "PollStore":
		"""
		Initiate PollStore object.
		"""
		super(PollStore, self).__init__(Poll)

	def create(self, title: str, description: str, image_id: int) -> Poll:
		"""
		Create and return Poll.
		"""
		return super().create(
			title=title, description=description, image_id=image_id
		)

	def update(self, uid: str,
						 title: str, description: str, image_id: int) -> Poll:
		"""
		Update and return Poll.
		"""
		return super().update(
			uid=uid, title=title, description=description, image_id=image_id
		)

	def set_data_uid(self, uid: str, data_uid: str) -> Poll:
		"""
		Set data uid and return Poll.
		"""
		return super().update(
			uid=uid, data_uid=data_uid
		)

	def set_vote_data(self, uid: str, vote_data: str) -> Poll:
		"""
		Set vote_data and return Poll.
		"""
		return super().update(
			uid=uid, vote_data=vote_data
		)

	def read_list(self, offset: int, limit: int,
							  title: str, description: str,
								data_uid: str = None) -> (int, list):
		"""
		Return total number and list of Polls by arguments.
		"""
		query = database.session.query(
			Poll, File
		).join(
			File, File.id == Poll.image_id
		).filter(
			True if title is None else \
				Poll.title.contains(title),
			True if description is None else \
				Poll.description.contains(description),
			True if data_uid is None else \
				Poll.data_uid == data_uid,
			Poll.deleted_utc == None
		).order_by(
			Poll.modified_utc.desc()
		)
		return (
			self.count(query),
			query.limit(limit).offset(offset).all()
		)
