from flask_mail import Message
from app import mail, db
from threading import Thread
from flask import current_app
from app.models import MailActivity
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def send_async_email(app, msg):
    with app.app_context():
        client = boto3.client('ses', region_name='us-east-1', aws_access_key_id='current_app.config.get('AWS_ACCESS')',
                              aws_secret_access_key='current_app.config.get('AWS_SECRET')')
        response = client.send_email(Destination={'ToAddresses': msg.recipients},
                                     Message={
                                        'Body': {
                                            'Html': {
                                                'Charset': "UTF-8",
                                                'Data': msg.html,
                                            },
                                            'Text': {
                                                'Charset': "UTF-8",
                                                'Data': msg.body,
                                            },
                                        },
                                        'Subject': {
                                            'Charset': "UTF-8",
                                            'Data': msg.subject,
                                        },
                                    },
                                     Source=msg.sender,
                                     ConfigurationSetName='ILMJTCV')


def send_async_email_special(app, msg):
    with app.app_context():
        client = boto3.client('ses', region_name='us-east-1', aws_access_key_id='current_app.config.get('AWS_ACCESS')',
                              aws_secret_access_key='current_app.config.get('AWS_SECRET')')
        print(msg)
        response = client.send_raw_email(
            Source=msg['From'],
            Destinations=[
                msg['To']
            ],
            RawMessage={
                'Data': msg.as_string(),
            },
            ConfigurationSetName='ILMJTCV'
        )


def send_email(subject, sender, recipients, text_body, html_body=None, bcc=None):
    msg = Message(subject, sender=sender, recipients=recipients, bcc=bcc)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def send_special_email(subject, sender, recipients, text_body, attachments=None, html_body=None, bcc=None):
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg_body = MIMEMultipart('alternative')
    textpart = MIMEText(text_body.encode("utf-8"), 'plain', "utf-8")
    htmlpart = MIMEText(html_body.encode("utf-8"), 'html', "utf-8")
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    msg.attach(msg_body)
    for attachment in attachments:
        att = MIMEApplication(open(attachment, 'rb').read())
        att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
        msg.attach(att)
        os.remove(path=attachment)
    Thread(target=send_async_email_special, args=(current_app._get_current_object(), msg)).start()


def add_activity(user, type):
    activity = MailActivity(user_id=user.id, type=type)
    db.session.add(activity)
    db.session.commit()


import boto3
from botocore.exceptions import ClientError
