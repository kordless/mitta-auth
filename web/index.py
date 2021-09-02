import datetime
import os
import re

import requests
import urllib
import json

from google.cloud import ndb

from flask import Blueprint, request, make_response, render_template, abort
import flask_login

from web.models import Sidekick

from lib.solr import add_document
from lib.builder import Builder
from lib.util import random_string

import config

index_handlers = Blueprint('index', __name__)

# client connection
client = ndb.Client()

# create a new sidekick for the user
@index_handlers.route('/i', methods=['POST'])
@flask_login.login_required
def create():
	# timestamp everything
	now = datetime.datetime.now()
	timestring = "%Y-%m-%dT%H:%M:%SZ"
	timestamp = now.strftime(timestring)

	sidekick_count = len(Sidekick.get_all(uid=flask_login.current_user.uid))

	if sidekick_count > 7: # needs to be a user config setting TODO
		# limit adding
		response = make_response(
			render_template(
				'api/sidekick_error.json',
				timestamp=timestamp,
				message="Over quota for sidekicks.",
				request_url="/i"
			)
		)
	
		response.headers['Content-Type'] = 'application/json'

		return response, 405

	# otherwise create a new one
	sidekick = Sidekick.create(uid=flask_login.current_user.uid)

	with client.context():
		response = make_response(
			render_template(
				'api/sidekick.json', 
				timestamp=timestamp,
				sidekick=sidekick,
				request_url="/i"
			)
		)

	response.headers['Content-Type'] = 'application/json'

	return response


# get a list of user's sidekicks
@index_handlers.route('/i', methods=['GET'])
@flask_login.login_required
def list():
	# timestamp everything
	now = datetime.datetime.now()
	timestring = "%Y-%m-%dT%H:%M:%SZ"
	timestamp = now.strftime(timestring)

	sidekicks = Sidekick.get_all(uid=flask_login.current_user.uid)
	
	with client.context():
		response = make_response(
			render_template(
				'api/sidekicks.json',
				timestamp=timestamp, 
				sidekicks=sidekicks,
				request_url="/i"
			)
		)

	response.headers['Content-Type'] = 'application/json'

	return response


# get sidekick status
@index_handlers.route('/i/<nick>', methods=['GET'])
@flask_login.login_required
def status(nick=""):
	# timestamp everything
	now = datetime.datetime.now()
	timestring = "%Y-%m-%dT%H:%M:%SZ"
	timestamp = now.strftime(timestring)

	sidekick = Sidekick.get_by_uid_nick(uid=flask_login.current_user.uid, nick=nick)
	
	if not sidekick:
		# limit adding
		response = make_response(
			render_template(
				'api/sidekick_error.json',
				timestamp=timestamp,
				message="Sidekick not found",
				request_url="/i/%s" % nick
			)
		)

		response.headers['Content-Type'] = 'application/json'

		return response, 404

	with client.context():
		response = make_response(
			render_template(
				'api/sidekick.json', 
				timestamp=timestamp,
				sidekick=sidekick,
				request_url="/i/%s" % nick
			)
		)

	response.headers['Content-Type'] = 'application/json'

	return response


# DELETE
# delete a single sidekick
@index_handlers.route('/i/<nick>', methods=['DELETE'])
@flask_login.login_required
def delete(nick=""):
	uid = flask_login.current_user.uid

	with client.context():
		try:
			sidekick = Sidekick.query().filter(Sidekick.uid==uid, Sidekick.nick==nick).get()
			name = sidekick.name
			sidekick.key.delete()

			try:
				response = requests.get(
					"%sadmin/cores?action=UNLOAD&core=%s&deleteInstanceDir=true"
					 % ((config.solr_url, name)))
				print(response.text)

			except Exception as ex:
				raise Exception("%s while deleting index and/or directories." % ex)

			return json.dumps({"result": "success"}), 200

		except Exception as ex:
			print(str(ex))
			# need to set the content-type?
			return json.dumps({"result": "Error %s. Maybe this sidekick doesn't exist?" % ex}), 405


# index a document
@index_handlers.route('/i/<nick>', methods=['POST'])
@flask_login.login_required
def index(nick=""):
	# timestamp everything
	now = datetime.datetime.now()
	timestring = "%Y-%m-%dT%H:%M:%SZ"
	timestamp = now.strftime(timestring)

	# get the documents from the request
	json_documents = request.get_json()

	# need to create a text or words field that has all words from title, description, url, etc.
	num_docs_indexed = 0

	sidekick = Sidekick.get_by_uid_nick(uid=flask_login.current_user.uid, nick=nick)

	if not sidekick:
		# limit adding
		response = make_response(
			render_template(
				'api/sidekick_error.json',
				timestamp=timestamp,
				message="Sidekick not found",
				request_url="/i/%s" % nick
			)
		)

		response.headers['Content-Type'] = 'application/json'

		return response, 404

	for document in json_documents['response']:
		solr_response = add_document(
			document, 
			sidekick.name
		)

		num_docs_indexed = num_docs_indexed + 1

	# look at responses for errors?

	response = make_response(
		render_template(
			'api/index_response.json',
			timestamp=timestamp,
			request_url="/i/%s" % nick,
			num_docs_indexed = num_docs_indexed
		)
	)

	response.headers['Content-Type'] = 'application/json'
	
	return response


# DELETE DOCUMENT
# delete a sidekick's document
@index_handlers.route('/i/<nick>/<doc_id>', methods=['DELETE'])
@flask_login.login_required
def delete_document(nick="", doc_id=""):
	# timestamp everything
	now = datetime.datetime.now()
	timestring = "%Y-%m-%dT%H:%M:%SZ"
	timestamp = now.strftime(timestring)

	uid = flask_login.current_user.uid

	sidekick = Sidekick.get_by_uid_nick(uid=flask_login.current_user.uid, nick=nick)
	
	if not sidekick:
		# limit adding
		response = make_response(
			render_template(
				'api/sidekick_error.json',
				timestamp=timestamp,
				message="Sidekick not found",
				request_url="/i/%s" % nick
			)
		)

		response.headers['Content-Type'] = 'application/json'

		return response, 404

	try:
		response = requests.post(
			"%s%s/update?commit=true" % (config.solr_url, sidekick.name),
			data = json.dumps({"delete": {"id":"%s" % doc_id}}),
			headers = {"content-type": "application/json"},
			timeout = 3
		)
		
	except Exception as ex:
		return json.dumps({"result": "Error %s." % ex}), 405

	return json.dumps({"result": "success"}), 200