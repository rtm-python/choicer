# -*- coding: utf-8 -*-

'''
Store module for Option entity.
'''

# Standard libraries import
from datetime import datetime

# Application modules import
from models import database
from models import Store
from models.entity.option import Option
from models.entity.file import File

# Additional libraries import
from sqlalchemy import and_


class OptionStore(Store):
	"""
	This is a OptionStore class.
	"""

	def __init__(self) -> "OptionStore":
		"""
		Initiate OptionStore object.
		"""
		super(OptionStore, self).__init__(Option)

	def create(self, poll_id: int,
						 title: str, description: str, image_id: int) -> Option:
		"""
		Create and return Option.
		"""
		return super().create(
			poll_id=poll_id,
			title=title, description=description, image_id=image_id,
			order_utc=datetime.utcnow()
		)

	def update(self, uid: str,
						 title: str, description: str, image_id: int) -> Option:
		"""
		Update and return Option.
		"""
		return super().update(
			uid=uid, title=title, description=description, image_id=image_id
		)

	def reorder(self, uid: str, order_utc: datetime) -> Option:
		"""
		Update order_utc and return Option.
		"""
		return super().update(
			uid=uid, order_utc=order_utc
		)

	def read_list(self, poll_id: int,
								offset: int, limit: int,
								title: str, description: str) -> (int, list):
		"""
		Return total number and list of Options by arguments.
		"""
		query = database.session.query(
			Option, File
		).join(
			File, File.id == Option.image_id
		).filter(
			True if poll_id is None else \
				Option.poll_id == poll_id,
			True if title is None else \
				Option.title.contains(title),
			True if description is None else \
				Option.description.contains(description),
			Option.deleted_utc == None
		).order_by(
			Option.order_utc.desc()
		)
		return (
			self.count(query),
			query.limit(limit).offset(offset).all()
		)
