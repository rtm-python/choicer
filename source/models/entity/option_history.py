# -*- coding: utf-8 -*-

'''
Entity module for Option history entity.
'''

# Additional libraries import
from sqlalchemy import Column
from sqlalchemy import ForeignKey

# Project modules imports
from models import database
from models.entity import Entity


class OptionHistory(Entity):
	"""
	This is a class for Option entity.
	"""
	__tablename__ = 'option_history'
	user_id = Column(
		database.Integer, ForeignKey('user.id'),
		index=True, nullable=False
	)
	option_id = Column(
		database.Integer, ForeignKey('option.id'),
		index=True, nullable=False
	)
	event = Column(database.String, index=True, nullable=True)

	def __init__(self, user_id: int, option_id: int,
							 event: str) -> "OptionHistory":
		"""
		Initiate object and stores OptionHistory's data.
		"""
		super().__init__()
		self.user_id = user_id
		self.option_id = option_id
		self.event = event
