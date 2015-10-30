from flask_wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, HiddenField


class EmailSendForm(Form):
    email = TextField("Address")
    message = TextAreaField("Extra Message")
    submit = SubmitField("Send Email")
    urldata = HiddenField("Url Data")
