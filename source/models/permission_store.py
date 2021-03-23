# -*- coding: utf-8 -*-

"""
Store module for permission entity.
"""

# Stabdard libraries import
from datetime import datetime

# Application modules import
from models import database
from models import Store
from models.entity.permission import Permission

# Additional libraries import
from sqlalchemy import and_
from sqlalchemy import or_


class PermissionStore(Store):
	"""
	This is a permission class.
	"""

	def __init__(self) -> "PermissionStore":
		"""
		Initiate PermissionStore object.
		"""
		super(PermissionStore, self).__init__(Permission)

	def create(self, user_id: int, value: str) -> Permission:
		"""
		Create and return permission.
		"""
		return super().create(
			user_id=user_id, value=value
		)

	def update(self, uid: str, user_id: int, value: str) -> Permission:
		"""
		Update and return permission.
		"""
		return super().update(
			uid=uid, user_id=user_id, value=value
		)

	def read_list(self, offset: int, limit: int,
							  user_id: int, value: str) -> list:
		"""
		Return total number and list of permission by arguments.
		"""
		query = database.session.query(
			Permission
		).filter(
			True if user_id is None else \
				Permission.user_id == user_id,
			True if value is None else \
				Permission.value == value,
			Permission.deleted_utc == None
		).order_by(
			Permission.modified_utc.desc()
		)
		return (
			self.count(query),
			query.limit(limit).offset(offset).all()
		)
