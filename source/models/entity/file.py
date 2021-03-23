# -*- coding: utf-8 -*-

"""
Entity module for permission entity.
"""

# Additional libraries import
from sqlalchemy import Column

# Project modules imports
from models import database
from models.entity import Entity


class File(Entity):
	"""
	This is a class for File entity.
	"""
	__tablename__ = 'file'
	title = Column(database.String, index=True, nullable=False)
	name = Column(database.String, index=True, nullable=False)
	type = Column(database.String, index=True, nullable=False)
	path = Column(database.String, index=True, nullable=False)
	size = Column(database.Integer, index=True, nullable=False)

	def __init__(self, title: str,
							 name: str, type: str, path: str, size: int) -> "File":
		"""
		Initiate object and stores File's data.
		"""
		super().__init__()
		self.title = title
		self.name = name
		self.type = type
		self.path = path
		self.size = size
