import os
import sys
import datetime
import requests
import json
import io

from flask import Blueprint, render_template
from flask import make_response, Response
from flask import redirect, url_for, abort
from flask import request, send_file

import flask_login

from google.cloud import storage
from google.cloud import ndb

site = Blueprint('site', __name__)

from web.models import User

from lib.util import random_string

from web.models import Transaction

import config

# client connection
client = ndb.Client()

def get_uid():
	try:
		uid = flask_login.current_user.uid
	except:
		uid = "anonymous"

	return uid


# routes must be specified because we handle all routes for bookmarking by adding mitta.us/
@site.route('/')
def index():
	return render_template('pages/index.html', config=config, uid=get_uid())

@site.route('/robots.txt')
def robots():
	return "User-agent: *\r\nAllow: /"

@site.route('/legal')
@flask_login.login_required
def legal():
	return render_template('pages/legal.html', config=config, uid=get_uid())


@site.route('/a', methods=['GET'])
@flask_login.login_required
def token():
	response = make_response(
		render_template(
			'api/token.json', 
			json = json.dumps(
				{
					'token': '%s' % flask_login.current_user.api_token
				}
			)
		)
	)
	response.headers['Content-Type'] = 'application/json'
	return response


@site.route('/a', methods=['POST'])
@flask_login.login_required
def token_reset():
	# rotate the token
	User.token_reset(flask_login.current_user.uid)

	response = make_response(
		render_template(
			'token.json', 
			json = json.dumps(
				{
					'token': '%s' % flask_login.current_user.api_token
				}
			)
		)
	)
	response.headers['Content-Type'] = 'application/json'
	return response


# health check for login status
@site.route('/h')
def health():
	try:
		uid = flask_login.current_user.uid
	except:
		uid = "anonymous"
	
	response = make_response(
		render_template(
			'api/health.json',
			json = json.dumps({"result": "success", "uid": uid})
		)
	)
	response.headers['Content-Type'] = 'application/json'
	return response


# url post paste handler
@site.route('/<path:path>')
@flask_login.login_required
def paste(path):
	url = "%s?%s" % (path, request.query_string.decode("utf-8"))
	import re
	if not re.match('(?:http|ftp|https)://', url):
		url = 'http://{}'.format(url)
		
	# process line with builder
	transaction_id = random_string(13)
	transaction = Transaction.create(uid=flask_login.current_user.uid, tid=transaction_id)

	try:
		return redirect(url)
	except:
		abort(404, description="resource not found")


# image serving
@site.route('/d/<name>/<filename>')
@flask_login.login_required
def serve(name, filename):
	uid = flask_login.current_user.uid

	# get the user's spools
	spool = Spool.get_by_uid_name(uid, name)

	if not spool:
		abort(404, description="document not found")

	try:
		# use bucket on google cloud
		gcs = storage.Client()
		bucket = gcs.bucket(config.cloud_storage_bucket)
		blob = bucket.blob("%s/%s/%s" % (uid, spool.name, filename))

		buffer = io.BytesIO()
		blob.download_to_file(buffer)
		buffer.seek(0)

		return send_file(
			buffer, 
			attachment_filename=filename, 
			as_attachment=False,
			mimetype=blob.content_type # and there it is
		)

	except Exception as ex:
		print(ex)
		abort(404, description="document not found")

	return Response(blob)