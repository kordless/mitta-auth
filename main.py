import datetime
import logging
import os
import json

# different buckets for dev vs. production
from google.cloud import storage
from google.cloud import ndb

from flask import Flask, session, request, render_template
from flask_talisman import Talisman
import flask_login

from web.models import User, Transaction

from web.site import site
from web.auth import auth
from web.search import search_handlers

import config
 
# storage
CLOUD_STORAGE_BUCKET = config.cloud_storage_bucket

# app up
app = Flask(__name__)
app.secret_key = config.secret_key

@app.template_filter('json_dumps')
def json_dumps(value):
	print(value)
	return json.dumps(value, sort_keys=True, indent=2)

# logins
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_message = u"Please provide the requested credentials."


# client connection
client = ndb.Client()

@login_manager.request_loader
def load_request(request):
	# GETs send args
	token = request.args.get('token')

	# might be a POST
	if not token:
		token = request.form.get('token')

	if token:
		with client.context():
			user = User.query().filter(User.api_token==token).get()
		return user
	else:
		return None

@login_manager.user_loader 
def load_user(uid):
	with client.context():
		return User.query().filter(User.uid==uid).get()


# enforce SSL on prod
if config.dev == "False":
	# mitta.us/s?q='csp allow inline Scripts'
	Talisman(app, content_security_policy=None)	


# auth, api and shell blueprints
app.register_blueprint(site)
app.register_blueprint(auth)
app.register_blueprint(search_handlers)

# this
# login_manager.login_view = "auth.login"
# or this
login_manager.blueprint_login_views = {
	'site': "/login",
	'shell': "/login"
}

@app.errorhandler(404)
def f404_notfound(e):
	logging.info("here")
	return "404 not found <a href='/'>exit</a>", 404

@app.errorhandler(401)
def api_auth_fail(e):
	return json.dumps({"result": "error", "response": "Invalid token."}), 401

@app.errorhandler(500)
def server_error(e):
	# handle a 404 too!
	logging.exception('An error occurred during a request.')
	return "An error occured and this is the fail.".format(e), 500

@app.before_request
def hard_session():
	session.permanent = True
	app.permanent_session_lifetime = config.login_lifetime

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


if __name__ == '__main__':
	# This is used when running locally. Gunicorn is used to run the
	# application on Google App Engine. See entrypoint in app.yaml.
	app.run(host='127.0.0.1', port=8080, debug=True)
	dev = True
