# -*- coding: utf-8 -*-

"""
Utility module to handle lists.
"""

# Standard libraries import
import math

# Application modules import
import blueprints

# Additional libraries import
from flask import request
from flask import url_for

DEFAULT_PER_PAGE = 12


class Pagination():
	"""
	This is a Pagination class to handle pages.
	"""
	name = None
	name_page_index = None
	name_per_page = None
	endpoint = None
	kwargs = None
	page_index = None
	per_page= None
	page_count = None
	entity_count = None

	def __init__(self, name: str, endpoint: str, **kwargs) -> "Pagination":
		"""
		Initiate pagination object with values.
		"""
		# Apply pagination naming
		self.name = name
		self.name_page_index = '%sPageIndex' % name
		self.name_per_page = '%sPerPage' % name
		# Get page_index and per_page from request
		self.page_index = blueprints.get_value(
			self.name_page_index, int, 1)
		self.per_page = blueprints.get_value(
			self.name_per_page, int, DEFAULT_PER_PAGE)
		self.endpoint = endpoint
		self.kwargs = kwargs

	def validate(self, entity_count: int) -> "Pagination":
		"""
		Initiate pagination object with values.
		"""
		is_valid = True
		self.entity_count = entity_count
		# Calculate page_count
		self.page_count = int(math.modf(entity_count / self.per_page)[1])
		if self.page_count < self.entity_count / self.per_page:
			self.page_count = self.page_count + 1
		# Check page_index and per_page validity
		if self.page_index < 1:
			self.page_index = 1
			is_valid = False
		elif self.page_index > self.page_count:
			self.page_index = self.page_count
			is_valid = False
		if self.per_page < 1:
			self.per_page = 1
			is_valid = False
		# Store arguments in session
		blueprints.set_value(self.name_page_index, self.page_index)
		blueprints.set_value(self.name_per_page, self.per_page)
		return is_valid

	def url_for(self, page_index: int = None, per_page: int = None,
							on_verified_pages: bool = False) -> str:
		"""
		Return url_for defined page_index.
		"""
		verify_page_index = self.page_index \
			if page_index is None else page_index
		verify_per_page = self.per_page \
			if per_page is None else per_page
		if on_verified_pages and \
				(
					verify_page_index < 1 or \
					verify_page_index > self.page_count or \
					verify_per_page < 1
				):
			return
		return url_for(
			self.endpoint,
			**{
				self.name_page_index: page_index,
				self.name_per_page: per_page,
				**self.kwargs
			}
		)

	def url_for_prev(self) -> str:
		"""
		Return url_for for previous page (if possible).
		"""
		return self.url_for(
			page_index=self.page_index - 1, on_verified_pages=True)

	def url_for_next(self) -> str:
		"""
		Return url_for for next page (if possible).
		"""
		return self.url_for(
			page_index=self.page_index + 1, on_verified_pages=True)
