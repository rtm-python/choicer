# -*- coding: utf-8 -*-

'''
Entity module for Poll history entity.
'''

# Additional libraries import
from sqlalchemy import Column
from sqlalchemy import ForeignKey

# Project modules imports
from models import database
from models.entity import Entity


class PollHistory(Entity):
	"""
	This is a class for Poll entity.
	"""
	__tablename__ = 'poll_history'
	user_id = Column(
		database.Integer, ForeignKey('user.id'),
		index=True, nullable=False
	)
	poll_id = Column(
		database.Integer, ForeignKey('poll.id'),
		index=True, nullable=False
	)
	event = Column(database.String, index=True, nullable=True)

	def __init__(self, user_id: int, poll_id: int,
							 event: str) -> "PollHistory":
		"""
		Initiate object and stores PollHistory's data.
		"""
		super().__init__()
		self.user_id = user_id
		self.poll_id = poll_id
		self.event = event
