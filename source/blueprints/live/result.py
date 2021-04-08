# -*- coding: utf-8 -*-

"""
Service module to handle Poll catalog.
"""

# Standard libraries import
import logging
import json

# Application modules import
import blueprints
from plugins.choicer import Plugin as ChoicerPlugin
from models.poll_store import PollStore
from models.entity.poll import Poll


class Result():
	"""
	This is a Result class to handle poll's results.
	"""

	@staticmethod
	def get_poll(uid: str) -> Poll:
		"""
		Return poll by uid.
		"""
		return PollStore().read(uid)

	@staticmethod
	def get_last_poll() -> Poll:
		"""
		Return last updated poll entity.
		"""
		poll_store = PollStore()
		poll_count, poll_list = poll_store.read_list(None, 1, None, None)
		if len(poll_list) == 0:
			return None
		return poll_list[0][0]

	@staticmethod
	def get_last_results() -> str:
		"""
		Return results for last poll.
		"""
		poll = Result.get_last_poll()
		return Result.get_results(poll)

	@staticmethod
	def get_vote_data(poll: Poll) -> dict:
		"""
		Return vote data for poll by uid.
		"""
		if poll is None:
			return ''
		if poll.data_uid is None:
			vote_data = json.loads(poll.vote_data)
		else:
			vote_data = ChoicerPlugin.read_poll(poll.data_uid)
		return vote_data

	@staticmethod
	def get_results(poll: Poll) -> str:
		"""
		Return raw results for poll by uid.
		"""
		vote_data = Result.get_vote_data(poll)
		results = [
			'%d|%d|%s|%s' % (
				option['count'], option['percent'], option['image']['uid'], option['title']
			) for option in vote_data['results']
		]
		return '\r\n'.join([str(vote_data['voters']['count'])] + results)
