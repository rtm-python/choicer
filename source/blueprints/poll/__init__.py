# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate Poll blueprint.
"""

# Standard libraries import
import os

# Application modules import
import blueprints
from plugins.admin import permission_required
from config import STATIC_PATH

# Additional libraries import
from flask import Blueprint
from flask import url_for
from flask import request
from flask import redirect
from flask import render_template
from flask_login import current_user

# Initiate Blueprint object
blueprint = Blueprint(
	'poll', __name__,
	static_folder=STATIC_PATH,
	template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)

# Routes handling modules import
from blueprints.poll import poll_catalog
from blueprints.poll import poll_history
from blueprints.poll import poll_form


@blueprint.route('/', methods=('GET', 'POST'))
@blueprint.route('/catalog/', methods=('GET', 'POST'))
#@permission_required
def get_catalog():
	"""
	Return poll catalog page.
	"""
	filter = poll_catalog.PollFilter()
	if filter.form_valid:
		if filter.submit.data:
			return redirect(url_for('poll.get_catalog'))
		elif filter.reset.data:
			filter.reset_fields()
			return redirect(url_for('poll.get_catalog'))
	reorderer = poll_catalog.ReordererForm()
	if reorderer.form_valid:
		if reorderer.submit.data:
			reorderer.reorder()
			return redirect(url_for('poll.get_catalog'))
	pagination, list = poll_catalog.PollList(
		'poll.get_catalog').read_list(filter)
	return render_template(
		'poll_catalog.html',
		list=list,
		filter=filter,
		pagination=pagination,
		reorderer=reorderer
	)


@blueprint.route('/history/', methods=('GET', 'POST'))
#@permission_required
def get_history():
	"""
	Return poll history page.
	"""
	filter = poll_history.PollHistoryFilter()
	if filter.form_valid:
		if filter.submit.data:
			return redirect(url_for('poll.get_history'))
		elif filter.reset.data:
			filter.reset_fields()
			return redirect(url_for('poll.get_history'))
	pagination, list = poll_history.PollHistoryList(
		'poll.get_history').read_list(filter)
	return render_template(
		'poll_history.html',
		list=list,
		filter=filter,
		pagination=pagination
	)


@blueprint.route('/create/', methods=('GET', 'POST'))
#@permission_required
def create():
	"""
	Return poll create page.
	"""
	form = poll_form.PollForm()
	if form.form_valid:
		if form.submit.data:
			poll = form.create()
			poll_history.PollHistoryList.create(
				current_user.user.id, poll.id, 'create'
			)
			return redirect(url_for('poll.get_catalog'))
	return render_template(
		'poll_form.html',
		form=form,
		action=blueprints.__('Create')
	)


@blueprint.route('/update/<uid>/', methods=('GET', 'POST'))
#@permission_required
def update(uid: str):
	"""
	Return poll update page.
	"""
	form = poll_form.PollForm(uid)
	if form.form_valid:
		if form.submit.data:
			poll = form.update(uid)
			poll_history.PollHistoryList.create(
				current_user.user.id, poll.id, 'update'
			)
			return redirect(url_for('poll.get_catalog'))
	return render_template(
		'poll_form.html',
		form=form,
		action=blueprints.__('Update')
	)


@blueprint.route('/delete/<uid>/', methods=('GET',))
#@permission_required
def delete(uid: str):
	"""
	Delete poll by uid and return redirect to catalog.
	"""
	poll = poll_catalog.PollList.delete(uid)
	poll_history.PollHistoryList.create(
		current_user.user.id, poll.id, 'delete'
	)
	return redirect(url_for('poll.get_catalog'))
