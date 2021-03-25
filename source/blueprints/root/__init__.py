# -*- coding: utf-8 -*-

"""
Initial blueprint module to initiate base blueprint.
"""

# Standard libraries import
import os
import logging

# Application modules import
import blueprints
from blueprints.__form__ import FileForm
from config import STATIC_PATH
from config import TEMPLATE_PATH

# Additional libraries import
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask_login import logout_user
from flask_login import current_user

# Initiate Blueprint object
blueprint = Blueprint(
	'root', __name__,
	static_folder=STATIC_PATH,
	template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)

# Routes handling modules import
from blueprints.root import sign_form


@blueprint.route('/sign-in/', methods=('GET','POST'))
@blueprint.route('/identica/<url_token>/', methods=('GET','POST'))
@blueprint.route('/', methods=('GET','POST'))
def get_home(url_token: str = None):
	"""
	Return home page.
	"""
	if current_user.is_authenticated:
		return render_template('home.html')
	form = sign_form.SignInForm(url_token)
	if form.validate_on_submit():
		return form.authenticate() or \
			render_template(
				'home.html',
				form=form
			)
	return render_template(
		'home.html',
		form=form
	)


@blueprint.route('/sign-out/', methods=('GET',))
#@permission_required
def sign_out():
	"""
	Return home page after sign out.
	"""
	logout_user()
	return redirect(url_for('root.get_home'))


@blueprint.route('/upload/', methods=('POST',))
#@permission_required
def upload():
	"""
	Upload file and return result.
	"""
	return FileForm().upload()


@blueprint.route('/download/<uid>/', methods=('GET',))
#@permission_required
def download(uid: str):
	"""
	Return file by link.
	"""
	return FileForm.download(uid)


@blueprint.route('/site-map/', methods=('GET',))
def site_map():
	links = []
	for rule in blueprints.application.url_map.iter_rules():
		links.append(
			(
				rule.rule,
				rule.endpoint,
				str(rule.arguments) if len(rule.arguments) > 0 else None
			)
		)
	return {'links': links}, 200


@blueprints.application.errorhandler(400) # HTTP_400_BAD_REQUEST
@blueprints.application.errorhandler(401) # HTTP_401_UNAUTHORIZED
@blueprints.application.errorhandler(403) # HTTP_403_FORBIDDEN
@blueprints.application.errorhandler(404) # HTTP_404_NOT_FOUND
@blueprints.application.errorhandler(405) # HTTP_405_METHOD_NOT_ALLOWED
@blueprints.application.errorhandler(406) # HTTP_406_NOT_ACCEPTABLE
@blueprints.application.errorhandler(408) # HTTP_408_REQUEST_TIMEOUT
@blueprints.application.errorhandler(409) # HTTP_409_CONFLICT
@blueprints.application.errorhandler(410) # HTTP_410_GONE
@blueprints.application.errorhandler(411) # HTTP_411_LENGTH_REQUIRED
@blueprints.application.errorhandler(412) # HTTP_412_PRECONDITION_FAILED
@blueprints.application.errorhandler(413) # HTTP_413_REQUEST_ENTITY_TOO_LARGE
@blueprints.application.errorhandler(414) # HTTP_414_REQUEST_URI_TOO_LONG
@blueprints.application.errorhandler(415) # HTTP_415_UNSUPPORTED_MEDIA_TYPE
@blueprints.application.errorhandler(416) # HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
@blueprints.application.errorhandler(417) # HTTP_417_EXPECTATION_FAILED
@blueprints.application.errorhandler(428) # HTTP_428_PRECONDITION_REQUIRED
@blueprints.application.errorhandler(429) # HTTP_429_TOO_MANY_REQUESTS
@blueprints.application.errorhandler(431) # HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE
@blueprints.application.errorhandler(500) # HTTP_500_INTERNAL_SERVER_ERROR
@blueprints.application.errorhandler(501) # HTTP_501_NOT_IMPLEMENTED
@blueprints.application.errorhandler(502) # HTTP_502_BAD_GATEWAY
@blueprints.application.errorhandler(503) # HTTP_503_SERVICE_UNAVAILABLE
@blueprints.application.errorhandler(504) # HTTP_504_GATEWAY_TIMEOUT
@blueprints.application.errorhandler(505) # HTTP_505_HTTP_VERSION_NOT_SUPPORTED
def get_error(error):
	"""
	Return error page with error code.
	"""
	if getattr(error, 'code', 0) == 400:
		logging.error('Error Handler', exc_info=1)
	return render_template(
		'error.html', error_code=getattr(error, 'code', 0)
	), getattr(error, 'code', 200)
