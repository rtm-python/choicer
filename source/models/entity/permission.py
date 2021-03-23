# -*- coding: utf-8 -*-

"""
Entity module for permission entity.
"""

# Additional libraries import
from sqlalchemy import Column
from sqlalchemy import ForeignKey

# Project modules imports
from models import database
from models.entity import Entity


class Permission(Entity):
	"""
	This is a class for Permission entity.
	"""
	__tablename__ = 'permission'
	user_id = Column(
		database.Integer, ForeignKey('user.id'),
		index=True, nullable=False
	)
	value = Column(database.String, index=True, nullable=True)

	def __init__(self, user_id: int, value: str) -> "Permission":
		"""
		Initiate object and stores Permission's data.
		"""
		super().__init__()
		self.user_id = user_id
		self.value = value
