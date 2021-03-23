# -*- coding: utf-8 -*-

'''
Entity module for Option entity.
'''

# Standard libraries import
from datetime import datetime

# Additional libraries import
from sqlalchemy import Column
from sqlalchemy import ForeignKey

# Project modules imports
from models import database
from models.entity import Entity


class Option(Entity):
	"""
	This is a class for Option entity.
	"""
	__tablename__ = 'option'
	poll_id = Column(
		database.Integer, ForeignKey('poll.id'),
		index=True, nullable=True
	)
	title = Column(database.String, index=True, nullable=True)
	description = Column(database.String, index=True, nullable=True)
	image_filename = Column(database.String, index=True, nullable=True)
	order_utc = Column(database.DateTime, index=True, nullable=True)

	def __init__(self, poll_id: int, title: str,
							 description: str, order_utc: datetime) -> "Option":
		"""
		Initiate object and stores Option's data.
		"""
		super().__init__()
		self.poll_id = poll_id
		self.title = title
		self.description = description
		self.order_utc = order_utc
