# -*- coding: utf-8 -*-

"""
Store module for User entity.
"""

# Application modules import
from models import database
from models import Store
from models.entity.user import User


class UserStore(Store):
	"""
	This is a user store class.
	"""

	def __init__(self) -> "UserStore":
		"""
		Initiate UserStore object.
		"""
		super(UserStore, self).__init__(User)

	def create(self, from_id: str,
						 first_name: str, last_name: str, username: str) -> User:
		"""
		Create and return user.
		"""
		return super().create(
			from_id=from_id,
			first_name=first_name, last_name=last_name, username=username
		)

	def update(self, uid: str, from_id: str,
						 first_name: str, last_name: str, username: str) -> User:
		"""
		Update and return user.
		"""
		return super().update(
			uid=uid, from_id=from_id,
			first_name=first_name, last_name=last_name, username=username
		)

	def read_list(self, offset: int, limit: int,
							  from_id: str, filter_name: str) -> (int, list):
		"""
		Return total number and list of users by arguments.
		"""
		query = database.session.query(
			User
		).filter(
			True if from_id is None else \
				User.from_id.contains(from_id),
			True if filter_name is None else \
				User.first_name.contains(filter_name),
			User.deleted_utc == None
		).order_by(
			User.modified_utc.desc()
		)
		return (
			self.count(query),
			query.limit(limit).offset(offset).all()
		)

	def read_or_create_user(self, from_id: str,
													first_name: str, last_name: str,
													username: str) -> User:
		"""
		Return user by from_id or create if not exists (only not deleted).
		"""
		count, user_list = self.read_list(0, None, from_id, None)
		if count == 1:
			return user_list[0]
		return self.create(
			from_id=from_id,
			first_name=first_name, last_name=last_name, username=username
		)
