# -*- coding: utf-8 -*-

"""
Initial module to initiate database models and migrations.
"""

# Standard libraries import
import os
import importlib

# Additional libraries import
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Application modules import
from config import CONFIG
from config import DATABASE_PATH
from config import define_list
from blueprints import application

# Additional libraries import
from sqlalchemy import func

# Initiate database
database_folder = os.path.join(os.path.abspath(os.curdir), 'database')
if CONFIG['database']['filename'] is None:
	application.config['SQLALCHEMY_DATABASE_URI'] = \
		CONFIG['database']['URI']
else:
	application.config['SQLALCHEMY_DATABASE_URI'] = \
		CONFIG['database']['URI'] + \
		os.path.join(database_folder, CONFIG['database']['filename'])
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
database = SQLAlchemy(application)
migrate = Migrate(application, database, directory=database_folder)

# Entity modules import (prevent circular import)
# from models.entity import <entity_module>
from models.entity import Entity
for module_name in define_list('source/models/entity', '.py'):
	if not module_name.startswith('__'):
		module = importlib.import_module(
			'models.entity.%s' % module_name.split('.py')[0])


class Store():
	"""
	Abstract class for store objects.
	"""
	__abstract__ = True
	entity_class = None

	def __init__(self, entity_class: object) -> "Store":
		"""
		Initiate store object with entity object.
		"""
		self.entity_class = entity_class

	def create(self, **kwargs) -> Entity:
		"""
		Create and return entity.
		"""
		entity = self.entity_class(**kwargs)
		database.session.add(entity)
		database.session.commit()
		return entity

	def read(self, uid: str) -> Entity:
		"""
		Return entity by uid (only not deleted).
		"""
		return self.entity_class.query.filter_by(
			uid=uid, deleted_utc=None
		).first()

	def update(self, uid: str, **kwargs) -> Entity:
		"""
		Update and return entity (only not deleted).
		"""
		entity = self.read(uid)
		for key, value in kwargs.items():
			setattr(entity, key, value)
		entity.set_modified()
		database.session.commit()
		return entity

	def delete(self, uid: str) -> Entity:
		"""
		Delete and return entity (only not deleted).
		"""
		entity = self.read(uid)
		entity.set_deleted()
		database.session.commit()
		return entity

	def get(self, id: int) -> Entity:
		"""
		Return entity by id (no matter deleted or etc.).
		"""
		return self.entity_class.query.get(id)

	def count(self, query) -> int:
		"""
		Return number of elements (rows) in resulted query.
		"""
		return database.session.execute(
			query.statement.with_only_columns([func.count()]).order_by(None)
		).scalar() or 0
