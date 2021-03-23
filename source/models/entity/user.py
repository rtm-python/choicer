# -*- coding: utf-8 -*-

"""
Entity module for user entity.
"""

# Additional libraries import
from sqlalchemy import Column

# Project modules imports
from models import database
from models.entity import Entity


class User(Entity):
	"""
	This is a class for User entity.
	"""
	__tablename__ = 'user'
	from_id = Column(database.String, index=True, nullable=False)
	first_name = Column(database.String, index=True, nullable=True)
	last_name = Column(database.String, index=True, nullable=True)
	username = Column(database.String, index=True, nullable=True)

	def __init__(self, from_id: str,
							 first_name: str, last_name: str, username: str) -> "User":
		"""
		Initiate object and stores User's data.
		"""
		super().__init__()
		self.from_id = from_id
		self.first_name = first_name
		self.last_name = last_name
		self.username = username
