# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate Option blueprint.
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
	'option', __name__,
	static_folder=STATIC_PATH,
	template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)

# Routes handling modules import
from blueprints.option import option_catalog
from blueprints.option import option_history
from blueprints.option import option_form


@blueprint.route('/', methods=('GET', 'POST'))
@blueprint.route('/catalog/', methods=('GET', 'POST'))
#@permission_required
def get_catalog():
	"""
	Return option catalog page.
	"""
	filter = option_catalog.OptionFilter()
	if filter.form_valid:
		if filter.submit.data:
			return redirect(url_for('option.get_catalog'))
		elif filter.reset.data:
			filter.reset_fields()
			return redirect(url_for('option.get_catalog'))
	reorderer = option_catalog.ReordererForm()
	if reorderer.form_valid:
		if reorderer.submit.data:
			reorderer.reorder()
			return redirect(url_for('option.get_catalog'))
	pagination, list = option_catalog.OptionList(
		'option.get_catalog').read_list(filter)
	return render_template(
		'option_catalog.html',
		list=list,
		filter=filter,
		pagination=pagination,
		reorderer=reorderer
	)


@blueprint.route('/history/', methods=('GET', 'POST'))
#@permission_required
def get_history():
	"""
	Return option history page.
	"""
	filter = option_history.OptionHistoryFilter()
	if filter.form_valid:
		if filter.submit.data:
			return redirect(url_for('option.get_history'))
		elif filter.reset.data:
			filter.reset_fields()
			return redirect(url_for('option.get_history'))
	pagination, list = option_history.OptionHistoryList(
		'option.get_history').read_list(filter)
	return render_template(
		'option_history.html',
		list=list,
		filter=filter,
		pagination=pagination
	)


@blueprint.route('/create/', methods=('GET', 'POST'))
#@permission_required
def create():
	"""
	Return option create page.
	"""
	form = option_form.OptionForm()
	if form.form_valid:
		if form.submit.data:
			option = form.create()
			option_history.OptionHistoryList.create(
				current_user.user.id, option.id, 'create'
			)
			return redirect(url_for('option.get_catalog'))
	return render_template(
		'option_form.html',
		form=form,
		action=blueprints.__('Create')
	)


@blueprint.route('/update/<uid>/', methods=('GET', 'POST'))
#@permission_required
def update(uid: str):
	"""
	Return option update page.
	"""
	form = option_form.OptionForm(uid)
	if form.form_valid:
		if form.submit.data:
			option = form.update(uid)
			option_history.OptionHistoryList.create(
				current_user.user.id, option.id, 'update'
			)
			return redirect(url_for('option.get_catalog'))
	return render_template(
		'option_form.html',
		form=form,
		action=blueprints.__('Update')
	)


@blueprint.route('/delete/<uid>/', methods=('GET',))
#@permission_required
def delete(uid: str):
	"""
	Delete option by uid and return redirect to catalog.
	"""
	option = option_catalog.OptionList.delete(uid)
	option_history.OptionHistoryList.create(
		current_user.user.id, option.id, 'delete'
	)
	return redirect(url_for('option.get_catalog'))
