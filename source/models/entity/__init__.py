# -*- coding: utf-8 -*-

"""
Initial module to initiate entities.
"""

# Standard libraries import
import uuid
import datetime

# Application modules import
from models import database

# Additional libraries import
from sqlalchemy import Column


class Entity(database.Model):
	"""
	Abstract class for database entities with entity's id, uid,
	created_utc, modified_utc and deleted_utc fields.
	Also object string representation implemented.
	"""
	__abstract__ = True
	id = Column(database.Integer, primary_key=True)
	uid = Column(database.String)
	created_utc = Column(database.DateTime)
	modified_utc = Column(database.DateTime)
	deleted_utc = Column(database.DateTime)

	def __init__(self):
		"""
		Initiate object, generate uid for entity
		and set created utc value to current datetime.
		"""
		self.uid = str(uuid.uuid4())
		self.created_utc = datetime.datetime.utcnow()
		self.modified_utc = self.created_utc

	def set_modified(self):
		"""
		Set modified utc value to current datetime.
		"""
		self.modified_utc = datetime.datetime.utcnow()

	def set_deleted(self):
		"""
		Set deleted utc value to current datetime.
		"""
		self.deleted_utc = datetime.datetime.utcnow()
		self.modified_utc = self.deleted_utc

	def __str__(self):
		"""
		Generates object's string representation for possible debug purposes.
		"""
		return '\r\n'.join(
			['%s: %s' % (attr, getattr(self, attr))
				for attr in dir(self) if not attr.startswith('_') and \
					not callable(getattr(self, attr))]
		)
