# -*- coding: utf-8 -*-

'''
Entity module for Poll entity.
'''

# Standard libraries import
from datetime import datetime

# Additional libraries import
from sqlalchemy import Column
from sqlalchemy import ForeignKey

# Project modules imports
from models import database
from models.entity import Entity


class Poll(Entity):
	"""
	This is a class for Poll entity.
	"""
	__tablename__ = 'poll'
	title = Column(database.String, index=True, nullable=True)
	description = Column(database.String, index=True, nullable=True)
	image_id = Column(
		database.Integer, ForeignKey('file.id'),
		index=True, nullable=False
	)
	result = Column(database.String, index=True, nullable=True)
	status = Column(database.Boolean, index=True, nullable=True)

	def __init__(self, title: str, description: str, image_id: int) -> "Poll":
		"""
		Initiate object and stores Poll's data.
		"""
		super().__init__()
		self.title = title
		self.description = description
		self.image_id = image_id
