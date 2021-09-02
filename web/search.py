import os
import datetime
import json

import requests
import urllib

from google.cloud import ndb

from flask import Blueprint, request, make_response, render_template, abort
import flask_login

import config

# client connection
client = ndb.Client()

search_handlers = Blueprint('search_handlers', __name__)

# search
# @search_handlers.route('/s/id/<doc_id>')
@search_handlers.route('/s')
@flask_login.login_required
def search(nick = ""): 
	# request has context
	# timestamp everything
	now = datetime.datetime.now()
	timestring = "%Y-%m-%dT%H:%M:%SZ"
	timestamp = now.strftime(timestring)

	# if we have a line, request is likely from the shell
	line = request.args.get('line')
	
	if line:
		return line
	else:
		return "no line"

