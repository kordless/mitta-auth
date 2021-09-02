import datetime
import os
import requests

from google.cloud import ndb

import flask_login

from lib.util import random_string, random_number, generate_token

import config

# client connection
client = ndb.Client()

timestring = "%Y-%m-%dT%H:%M:%SZ"

# transactions allow one shot
class Transaction(ndb.Model):
	uid = ndb.StringProperty() # owner
	tid = ndb.StringProperty()
	created = ndb.DateTimeProperty()

	@classmethod
	def get_by_tid(cls, tid):
		with client.context():
			return cls.query(cls.tid == tid).get()

	@classmethod
	def create(cls, tid=None, uid=None):
		with client.context():
			cls(
				tid = tid,
				uid = uid,
				created = datetime.datetime.utcnow()
			).put()
			return cls.query(cls.tid == tid).get()


# user inherits from flask_login and ndb
class User(flask_login.UserMixin, ndb.Model):
	email = ndb.StringProperty()
	phone = ndb.StringProperty()
	phone_code = ndb.StringProperty(default=False)
	uid = ndb.StringProperty() # user_id
	api_token = ndb.StringProperty()
	mail_token = ndb.StringProperty()
	mail_confirm = ndb.BooleanProperty(default=False)
	mail_tries = ndb.IntegerProperty(default=0)
	authenticated = ndb.BooleanProperty(default=False)
	active = ndb.BooleanProperty(default=True)
	anonymous = ndb.BooleanProperty(default=False)
	paid = ndb.BooleanProperty(default=False)
	failed_2fa_attempts = ndb.IntegerProperty(default=0)
	created = ndb.DateTimeProperty()

	# flask-login
	def is_active(self): # all accounts are active
		return self.active

	def get_id(self):
		return self.uid

	def is_authenticated(self):
		return self.authenticated

	def is_anonymous(self):
		return self.anonymous

	@classmethod
	def token_reset(cls, uid=uid):
		with client.context():
			user = cls.query(cls.uid == uid).get()
			user.api_token = generate_token()
			user.put()
			return user

	@classmethod
	def create(cls, email="noreply@mitta.us", phone="+1"):
		with client.context():
			cls(
				email = email, 
				phone = phone,
				phone_code = generate_token(),
				created = datetime.datetime.utcnow(),
				uid = random_string(size=17),
				mail_token = generate_token(),
				api_token = generate_token()
			).put()

			from lib.solr import create_collection
			create_collection(cls.uid)

			return cls.query(cls.phone == phone, cls.email == email).get()

	@classmethod
	def get_by_email(cls, email):
		with client.context():
			return cls.query(cls.email == email).get()

	@classmethod
	def get_by_phone(cls, phone):
		with client.context():
			return cls.query(cls.phone == phone).get()

	@classmethod
	def get_by_mail_token(cls, mail_token):
		with client.context():
			return cls.query(cls.mail_token == mail_token).get()

	@classmethod
	def get_by_uid(cls, uid):
		with client.context():
			return cls.query(cls.uid == uid).get()

	@classmethod
	def get_by_token(cls, api_token):
		with client.context():
			return cls.query(cls.api_token == api_token).get()

