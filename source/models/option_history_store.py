# -*- coding: utf-8 -*-

'''
Store module for OptionHistory entity.
'''

# Application modules import
from models import database
from models import Store
from models.entity.option_history import OptionHistory
from models.entity.option import Option
from models.entity.user import User

# Additional libraries import
from sqlalchemy import or_


class OptionHistoryStore(Store):
	"""
	This is a OptionHistoryStore class.
	"""

	def __init__(self) -> "OptionHistoryStore":
		"""
		Initiate OptionHistoryStore object.
		"""
		super(OptionHistoryStore, self).__init__(OptionHistory)

	def create(self, user_id: int, option_id: int, event: str) -> Option:
		"""
		Create and return OptionHistory.
		"""
		return super().create(
			user_id=user_id, option_id=option_id, event=event
		)

	def update(self, uid: str,
						 user_id: int, option_id: int, event: str) -> Option:
		"""
		Update and return OptionHistory.
		"""
		return super().update(
			uid=uid, user_id=user_id, option_id=option_id, event=event
		)

	def read_list(self, poll_id: int,
								offset: int, limit: int,
							  username: str, title: str, event: str) -> (int, list):
		"""
		Return total number and list of OptionHistories by arguments.
		"""
		query = database.session.query(
			OptionHistory, User, Option
		).join(
			User, OptionHistory.user_id == User.id
		).join(
			Option, OptionHistory.option_id == Option.id
		).filter(
			True if username is None else \
				or_(
					User.first_name.contains(username),
					User.last_name.contains(username)
				),
			True if poll_id is None else \
				Option.poll_id == poll_id,
			True if title is None else \
				Option.title.contains(title),
			True if event is None else \
				OptionHistory.event.contains(event),
		).order_by(
			OptionHistory.modified_utc.desc()
		)
		return (
			self.count(query),
			query.limit(limit).offset(offset).all()
		)
