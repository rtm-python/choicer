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
from flask import render_template

# Initiate Blueprint object
blueprint = Blueprint(
	'live', __name__,
	static_folder=STATIC_PATH,
	template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)

# Routes handling modules import
from blueprints.live import result


@blueprint.route('/', methods=('GET',))
#@permission_required
def get_live():
	"""
	Return live last updated poll's results.
	"""
	poll = result.Result.get_last_poll()
	return render_template(
		'result.html',
		poll_title = poll.title,
		vote_data = result.Result.get_vote_data(poll)
	)


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
