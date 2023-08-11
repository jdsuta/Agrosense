import os
import requests
import urllib.parse
import sendgrid
from sendgrid import *
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash



# Including db use to validate
db = SQL("sqlite:///project.db")

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/

    References APIKEY: https://blog.teclado.com/api-key-authentication-with-flask/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if session.get("user_id") is None:
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function


def verify_api_key(api_key, devicename):
    # Perform the API key verification logic

    # Check the device name that the user input in the page apikey.html, and gets the API KEY then compares both.
    # we do this to avoid computational costs.

    rows = db.execute("SELECT * FROM devices WHERE device_name = ?;", devicename)
    print(rows)

    # Ensure devicename exists, is unique and apikey match
    if len(rows) != 1 or not check_password_hash(
        rows[0]["device_apikey"], api_key
    ):
        return False

    return True
    # Return True if the API key is valid, False otherwise

def emailwelcome(mail,username):
    #ref: https://docs.sendgrid.com/api-reference/mail-send/mail-send

    message = Mail(
        from_email='cs50_agrosense@thepanch.xyz',
        to_emails= To(mail)
        #html_content='<strong>and easy to do anywhere, even with Python</strong>'
        )
    message.dynamic_template_data = {
        'username': username
    }
    message.template_id = 'd-8621e600b85448af8313f817fb726380'
    message.asm = Asm(
        group_id=GroupId(18542),
        groups_to_display=GroupsToDisplay([18542])
    )

    try:
        sendgrid_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sendgrid_client.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(str(e))


def emailalarm(mail, username, devicename, temperature, humidity):
    #ref: https://docs.sendgrid.com/api-reference/mail-send/mail-send

    message = Mail(
        from_email='cs50_agrosense@thepanch.xyz',
        to_emails= To(mail)
        #html_content='<strong>and easy to do anywhere, even with Python</strong>'
        )
    message.dynamic_template_data = {
        'username' : username,
        'devicename': devicename,
        'temperature': temperature,
        'humidity': humidity
    }
    message.template_id = 'd-409f66b7f3374a949b032c6e7d369da9'
    message.asm = Asm(
        group_id=GroupId(18542),
        groups_to_display=GroupsToDisplay([18542])
    )

    try:
        sendgrid_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sendgrid_client.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(str(e))