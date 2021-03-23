# -*- coding: utf-8 -*-

"""
Module to handle plugin manager.
"""

# Standard libraries import
import logging
import importlib
import cProfile
import pstats
import io


class PluginManager():
	"""
	This PluginManager class describes managing for plugins.
	"""
	plugin = None

	def __init__(self, module_name: str, **kwargs) -> "PluginManager":
		"""
		Inititate PluginManager object with plugin name.
		"""
		self.plugin = importlib.import_module(
			'plugins.%s' % module_name).Plugin(**kwargs)
		logging.debug('PluginManager initiated with %s' % module_name)

	def execute(self, method_name: str, with_profile: bool = False):
		"""
		Execute plugin method by name and return method result.
		"""
		if with_profile:
			pr = cProfile.Profile()
			pr.enable()
			result = getattr(self.plugin, method_name)()
			pr.disable()
			s = io.StringIO()
			ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
			ps.print_stats()
			logging.debug(s.getvalue())
		else:
			result = getattr(self.plugin, method_name)()
		return result
