from flask import Flask
from flask import request
from flask import abort
from flask import render_template
from flask import json
from flask.ext.mail import Mail
from flask.ext.mail import Message

import jwt
import requests
from datetime import datetime
from dateutil import tz

from forms import EmailSendForm

app = Flask(__name__)
# app.config.from_envvar('APP_SETTINGS')
app.config.from_pyfile('config.cfg')
app.debug = True
app.secret_key = 'development key'

mail = Mail(app)

# Urllib3 import is for openshift environment. If you have decently new 2.7.x python,
# these are not needed and you can comment them.
# (https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning)
if app.config.get('USE_OPENSSL'):
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()



def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def call_api(token, url, payload):
    headers = {
        'Authorization': 'Token ' + token,
        'content-type': 'application/json'
    }

    r = requests.get(url, params=payload, headers=headers)

    if r.status_code != 200:
        raise r

    return r


def get_room(token, room_id):
    api_url = app.config.get('API_HOST') + "/api/v5/rooms/" + room_id
    response = call_api(token, api_url, {})
    room_data = json.loads(response.text)

    return room_data


def get_chat(token, chat_id):
    api_url = app.config.get('API_HOST') + "/api/v3/chat/chatsessions"
    response = call_api(token, api_url, {
        'since_id': chat_id,
        'page_size': 1
    })
    data = json.loads(response.text)

    return data


@app.context_processor
def utility_processor():
    def convert_timezone(time_str, timezone='Europe/Helsinki'):
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(timezone)
        utc = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')
        utc = utc.replace(tzinfo=from_zone)
        return utc.astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S")
    return dict(convert_timezone=convert_timezone)


def handle_jwt(data):
    return jwt.decode(data, app.config.get('APP_SECRET'))



@app.route('/send_email', methods=['POST'])
def send_email():
    form = EmailSendForm()
    jwt_data = handle_jwt(form.urldata.data)
    print jwt_data
    if request.method == 'POST':
        data = get_chat(app.config.get('API_TOKEN'), jwt_data['chat_id'])
        print data

        # check that we got conversation trough API
        if data['count'] != 1:
            return 'Email sending failed (API error).'

        if data['results'][0]['real_conversation'] is False:
            return render_template('ok.html')

        chat_data = data['results'][0]

        send_email("New chat conversation", "noreply@giosg.com", form.email,
            render_template("email.txt", data=chat_data),
            render_template("email.html", data=chat_data))

        #return 'Email posted.'


@app.route('/')
def chattomail():
    user = request.args.get('user')
    chat_id = request.args.get('chat')
    token = request.args.get('token')
    launch_type = request.args.get('type')

    if request.args.get('data') is None:
        return render_template('welcome.html')

    jwt_data = handle_jwt(request.args.get('data'))

    if launch_type == 'manual_dialog':
        form = EmailSendForm()
        form.urldata.data = request.args.get('data')
        return render_template('manual_dialog.html', form=form)
    elif launch_type == 'chat_end':
        data = get_chat(app.config.get('API_TOKEN'), jwt_data['chat_id'])

        # check that we got conversation trough API
        if data['count'] < 1:
            abort(404)

        if data['results'][0]['real_conversation'] is False:
            return render_template('ok.html')

        chat_data = data['results'][0]

        send_email("New chat conversation", "noreply@giosg.com", app.config.get('MAIL_RECEIVERS'),
            render_template("email.txt", data=chat_data),
            render_template("email.html", data=chat_data))
    else:
        abort(404)


    return render_template('ok.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
