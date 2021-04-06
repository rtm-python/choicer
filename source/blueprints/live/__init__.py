# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate Poll blueprint.
"""

# Standard libraries import
import os

# Application modules import
import blueprints
from config import STATIC_PATH

# Additional libraries import
from flask import Blueprint

# Initiate Blueprint object
blueprint = Blueprint(
	'live', __name__,
	static_folder=STATIC_PATH
)

# Routes handling modules import
from blueprints.live import result


@blueprint.route('/<uid>/', methods=('GET',))
#@permission_required
def get_results(uid: str):
	"""
	Return poll's results.
	"""
	return result.Result.get_results(
		result.Result.get_poll(uid))


@blueprint.route('/last/', methods=('GET',))
#@permission_required
def get_last_results():
	"""
	Return last updated poll's results.
	"""
	return result.Result.get_last_results()
