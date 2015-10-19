from flask import Flask
from flask import request
from flask import abort
from flask import render_template
from flask import json
from flask.ext.mail import Mail
from flask.ext.mail import Message

import requests
from datetime import datetime
from dateutil import tz

app = Flask(__name__)
app.config.from_envvar('APP_SETTINGS')
mail = Mail(app)


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
    api_url = "http://localhost:8000/api/v5/rooms/" + room_id
    response = call_api(token, api_url, {})
    room_data = json.loads(response.text)

    return room_data


def get_chat(token, chat_id):
    api_url = "http://localhost:8000/api/v3/chat/chatsessions"
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


@app.route('/')
def chattomail():
    api_token = '323e56fcdcc8b08c7a9a0dad5e9bff4c6dd68ed0'
    user = request.args.get('user')
    chat_id = request.args.get('chat')
    token = request.args.get('token')
    launch_type = request.args.get('type')

    if launch_type == 'chat_end':
        data = get_chat(api_token, chat_id)

        # check that we got conversation trough API
        if data['count'] < 1:
            abort(404)

        if data['results'][0]['real_conversation'] == False:
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
