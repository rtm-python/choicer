# -*- coding: utf-8 -*-

'''
Store module for PollHistory entity.
'''

# Application modules import
from models import database
from models import Store
from models.entity.poll_history import PollHistory
from models.entity.poll import Poll
from models.entity.user import User

# Additional libraries import
from sqlalchemy import or_


class PollHistoryStore(Store):
	"""
	This is a PollHistoryStore class.
	"""

	def __init__(self) -> "PollHistoryStore":
		"""
		Initiate PollHistoryStore object.
		"""
		super(PollHistoryStore, self).__init__(PollHistory)

	def create(self, user_id: int, poll_id: int, event: str) -> Poll:
		"""
		Create and return PollHistory.
		"""
		return super().create(
			user_id=user_id, poll_id=poll_id, event=event
		)

	def update(self, uid: str,
						 user_id: int, poll_id: int, event: str) -> Poll:
		"""
		Update and return PollHistory.
		"""
		return super().update(
			uid=uid, user_id=user_id, poll_id=poll_id, event=event
		)

	def read_list(self, offset: int, limit: int,
							  username: str, value: str, event: str) -> (int, list):
		"""
		Return total number and list of PollHistories by arguments.
		"""
		query = database.session.query(
			PollHistory, User, Poll
		).join(
			User, PollHistory.user_id == User.id
		).join(
			Poll, PollHistory.poll_id == Poll.id
		).filter(
			True if username is None else \
				or_(
					User.first_name.contains(username),
					User.last_name.contains(username)
				),
			True if value is None else \
				Poll.value.contains(value),
			True if event is None else \
				PollHistory.event.contains(event),
		).order_by(
			PollHistory.modified_utc.desc()
		)
		return (
			self.count(query),
			query.limit(limit).offset(offset).all()
		)
