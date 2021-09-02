# utilties
import os
import random
import string
import re
import secrets
import json

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# don't call yer methods Client, dorks
from twilio.rest import Client as Twilio

import config


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    print(filename.rsplit('.', 1)[1].lower())
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def random_number(size=6, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def random_string(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_token(size=64):
    # generate a secrets token, less the dashes for better copy pasta
    return secrets.token_urlsafe(size).replace('-','')


# test for an ipv6 address
def is_ipv6(addr):
    try:
        socket.inet_pton(socket.AF_INET6, addr)
        return True
    except socket.error:
        return False


def find_urls(text):
    # presumed valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,text)
    return [x[0] for x in url]


def clean_fulltext(text):
    import re

    text = text.replace('\n', ' ').replace('\r', ' ').replace('\s', ' ')

    return re.sub('[^a-zA-Z.\d\s]', '', text)


# sms user
def sms_user(phone_e164, message="Just saying Hi!"):
    try:
        client = Twilio(config.twilio_account_sid, config.twilio_auth_token)
        message = client.messages.create(
            body = message,
            from_ = config.twilio_number,
            to = phone_e164
        )
        return True
    except:
        return False

# email user
def email_user(email, subject="subject", html_content="content"):
    message = Mail(
        from_email='noreply@%s' % config.app_domain,
        to_emails=email,
        subject='%s' % subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(config.sendgrid_api_key)
        response = sg.send(message)
        
        if config.dev == "True":
            print(response.status_code)
            print(response.body)
            print(response.headers)

    except Exception as e:
        if config.dev == "True":
            print(e)
        
        response = {'status': "fail", 'message': "exception was %s" % e}

    return response