# -*- coding: utf-8 -*-

"""
Initial blueprint module to handle permission.
"""

# Standard libraries import
import os
import sys
import logging
from functools import wraps

# Application modules import
from models.permission_store import PermissionStore
from models.entity.permission import Permission
from models.user_store import UserStore
from models.entity.user import User
from config import define_list

# Additional libraries import
from flask_login import current_user
from flask import redirect
from flask import url_for


def get_permissions(user_id: int) -> list:
	"""
	Get permissions for user.
	"""
	return [
		permission.value \
			for permission in PermissionStore().read_list(
				0, None, user_id, None)[1]
	]


def add_permissions(user_id: int, permissions: list) -> None:
	"""
	Add permissions for user.
	"""
	current_permissions = get_permissions(user_id)
	for value in permissions:
		if value not in current_permissions:
			PermissionStore().create(user_id, value)
			current_permissions += [value]


def del_permissions(user_id: int, permissions: list) -> None:
	"""
	Del permissions for user.
	"""
	current_permissions = get_permissions(user_id)
	for value in permissions:
		if value in current_permissions:
			permission_list = PermissionStore().read_list(
				0, None, user_id, value)[1]
			PermissionStore().delete(permission_list[0].uid)
			current_permissions.remove(value)


def permission_required(function):
	"""
	User permission to access verification decorator.
	"""
	@wraps(function)
	def wrapper(*args, **kwargs):
		"""
		Wrapper function to verify user permission.
		"""
		if not current_user.is_authenticated or \
				current_user.user is None:
			logging.debug('Redirect unauthorized (anonymous) user')
			return redirect(url_for('root.get_home'))
		permission_value = '%s.%s' % (
			function.__module__,
			function.__name__
		)
		permissions = PermissionStore().read_list(
			0, None, current_user.user.id, permission_value)[1]
		if len(permissions) == 0:
			return redirect(url_for('root.get_home'))
		return function(*args, **kwargs)

	return wrapper


class Plugin():
	"""
	This Plugin class describes managing process
	on permission configuration.
	"""
	permissions = None

	def __init__(self, source_path: str) -> "Plugin":
		"""
		Initiate Plugin object.
		"""
		self.permissions = self.initiate_from_routes(
			os.path.join(source_path, 'blueprints'))

	def initiate_from_routes(self, folder: str) -> list:
		"""
		Read python files in folder and return list of
		permission_required occurencies.
		"""
		permissions = []
		packages = folder.replace('/', '.').split('source.', 1)[-1]
		for entry in os.listdir(folder):
			path = os.path.join(folder, entry)
			if entry.endswith('.py'):
				with open(path, 'r') as file:
					match = False
					for line in file:
						if line.strip() == '@permission_required':
							match = True
						elif match:
							match = False
							func_name = line.strip().split(' ')[-1].split('(', 1)[0]
							permissions += [
								'%s.%s.%s' % (packages, entry.split('.py', 1)[0], func_name)
							]
			elif os.path.isdir(path):
				permissions += self.initiate_from_routes(path)
		return permissions

	def configure(self) -> None:
		"""
		Configure permissions.
		"""
		user = None
		level = 0
		while True:
			print()
			choice = None
			choices = []
			# Display
			if level == 0:
				user = None
				users = UserStore().read_list(0, None, None, None)[1]
				choices = ['0: Exit'] + [
					'%d: %s (last login: %s) %s' % (
						index,
						' '.join([user.first_name, user.last_name]),
						user.modified_utc,
						user.uid
					) for index, user in enumerate(users, start=1)
				]
				choice = self.get_choice(choices)
			elif level == 1:
				choices = [
					'0: Back to users',
					'1: Add permission',
					'2: Delete permission',
					'3: Delete all permissions'
				]
				choice = self.get_choice(choices)
			elif level == 2:
				choices = ['0: Back to actions'] + [
					'%d: %s' % (
						index,
						permission
					) for index, permission in enumerate(
						self.permissions, start=1)
				]
				choice = self.get_choice(choices)
			elif level == 3:
				choices = ['0: Back to actions'] + [
					'%d: %s' % (
						index,
						permission
					) for index, permission in enumerate(
						get_permissions(user.id), start=1)
				]
				choice = self.get_choice(choices)
			# Choice
			if level == 0 and choice == 0:
				break
			elif level == 0 and choice > 0:
				user = UserStore().read(choices[choice].split()[-1])
				print('\n'.join(['Current permissions:'] + get_permissions(user.id)))
				level = 1
			elif level == 1 and choice == 0:
				user = None
				level = 0
			elif level == 1 and choice == 1:
				level = 2
			elif level == 1 and choice == 2:
				level = 3
			elif level == 1 and choice == 3:
				permissions = get_permissions(user.id)
				del_permissions(user.id, permissions)
				print('Deleted permissions: %s' % permissions)
				level = 1
			elif level == 2 and choice == 0:
				level = 1
			elif level == 2 and choice > 0:
				add_permissions(user.id, [choices[choice].split(' ')[1]])
				print('Added permission: %s' % choices[choice])
				level = 2
			elif level == 3 and choice == 0:
				level = 1
			elif level == 3 and choice > 0:
				del_permissions(user.id, [choices[choice].split(' ')[1]])
				print('Deleted permission: %s' % choices[choice])
				level = 3

	def get_choice(self, choices: list) -> int:
		"""
		Request user input and return integer value.
		"""
		while True:
			try:
				choice = int(input('\n'.join(choices) + '\n\nInput your choice: '))
				if choice < 0 or choice >= len(choices):
					raise ValueError()
				return choice
			except:
				print('Invalid choice, should be integer value in choices range\n')
