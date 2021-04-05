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
from blueprints.poll import option_catalog
from blueprints.poll import option_history
from blueprints.poll import option_form


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
	pagination, list = poll_catalog.PollList(
		'poll.get_catalog').read_list(filter)
	return render_template(
		'poll_catalog.html',
		list=list,
		filter=filter,
		pagination=pagination
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
		action=blueprints.__('Update'),
		poll_uid=uid,
		poll_active=False
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


@blueprint.route('/start/<uid>/', methods=('GET',))
#@permission_required
def start(uid: str):
	"""
	Start poll by uid.
	"""
	poll = poll_catalog.PollList.start(uid)
	poll_history.PollHistoryList.create(
		current_user.user.id, poll.id, 'start'
	)
	return redirect(url_for('poll.get_catalog'))


@blueprint.route('/stop/<uid>/', methods=('GET',))
#@permission_required
def stop(uid: str):
	"""
	Stop poll by uid.
	"""
	poll = poll_catalog.PollList.stop(uid)
	poll_history.PollHistoryList.create(
		current_user.user.id, poll.id, 'stop'
	)
	return redirect(url_for('poll.get_catalog'))


@blueprint.route('/<poll_uid>/option/', methods=('GET', 'POST'))
@blueprint.route('/<poll_uid>/option/catalog/', methods=('GET', 'POST'))
#@permission_required
def get_option_catalog(poll_uid: str):
	"""
	Return poll's option catalog page.
	"""
	filter = option_catalog.OptionFilter()
	if filter.form_valid:
		if filter.submit.data:
			return redirect(url_for('poll.get_option_catalog', poll_uid=poll_uid))
		elif filter.reset.data:
			filter.reset_fields()
			return redirect(url_for('poll.get_option_catalog', poll_uid=poll_uid))
	reorderer = option_catalog.ReordererForm()
	if reorderer.form_valid:
		if reorderer.submit.data:
			reorderer.reorder()
			poll_catalog.PollStore().set_vote_data(poll_uid, None)
			return redirect(url_for('poll.get_option_catalog', poll_uid=poll_uid))
	pagination, list = option_catalog.OptionList(
		'poll.get_option_catalog', poll_uid).read_list(poll_uid, filter)
	poll, file = poll_catalog.PollList.read(poll_uid)
	return render_template(
		'option_catalog.html',
		list=list,
		filter=filter,
		pagination=pagination,
		reorderer=reorderer,
		poll=poll,
		file=file
	)


@blueprint.route('/<poll_uid>/option/history/', methods=('GET', 'POST'))
#@permission_required
def get_option_history(poll_uid: str):
	"""
	Return poll's option history page.
	"""
	filter = option_history.OptionHistoryFilter()
	if filter.form_valid:
		if filter.submit.data:
			return redirect(url_for('poll.get_option_history', poll_uid=poll_uid))
		elif filter.reset.data:
			filter.reset_fields()
			return redirect(url_for('poll.get_option_history', poll_uid=poll_uid))
	pagination, list = option_history.OptionHistoryList(
		'poll.get_option_history', poll_uid).read_list(poll_uid, filter)
	return render_template(
		'option_history.html',
		list=list,
		filter=filter,
		pagination=pagination,
		poll_uid=poll_uid
	)


@blueprint.route('/<poll_uid>/option/create/', methods=('GET', 'POST'))
#@permission_required
def create_option(poll_uid: str):
	"""
	Return poll's option create page.
	"""
	form = option_form.OptionForm()
	if form.form_valid:
		if form.submit.data:
			option = form.create(poll_uid)
			option_history.OptionHistoryList.create(
				current_user.user.id, option.id, 'create'
			)
			poll_catalog.PollStore().set_vote_data(poll_uid, None)
			return redirect(url_for('poll.get_option_catalog', poll_uid=poll_uid))
	return render_template(
		'option_form.html',
		form=form,
		action=blueprints.__('Create'),
		poll_uid=poll_uid
	)


@blueprint.route('/<poll_uid>/option/update/<uid>/', methods=('GET', 'POST'))
#@permission_required
def update_option(poll_uid: str, uid: str):
	"""
	Return poll's option update page.
	"""
	form = option_form.OptionForm(uid)
	if form.form_valid:
		if form.submit.data:
			option = form.update(uid)
			option_history.OptionHistoryList.create(
				current_user.user.id, option.id, 'update'
			)
			poll_catalog.PollStore().set_vote_data(poll_uid, None)
			return redirect(url_for('poll.get_option_catalog', poll_uid=poll_uid))
	return render_template(
		'option_form.html',
		form=form,
		action=blueprints.__('Update'),
		poll_uid=poll_uid
	)


@blueprint.route('/<poll_uid>/option/delete/<uid>/', methods=('GET',))
#@permission_required
def delete_option(poll_uid: str, uid: str):
	"""
	Delete poll's option by uid and return redirect to option catalog.
	"""
	option = option_catalog.OptionList.delete(uid)
	option_history.OptionHistoryList.create(
		current_user.user.id, option.id, 'delete'
	)
	poll_catalog.PollStore().set_vote_data(poll_uid, None)
	return redirect(url_for('poll.get_option_catalog', poll_uid=poll_uid))
