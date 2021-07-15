import yaml
import smtplib
import operator
import requests

from functools import reduce
from abc import ABC, abstractmethod

from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import logging
logger = logging.getLogger(__name__)


class Config:

    def __init__(self, path: str) -> None:
        self.path = path
        self.read_config()

    def read_config(self):
        stream = open(self.path, 'r')
        self.config = yaml.load(stream, Loader=yaml.Loader)

    def get(self, *items):
        return reduce(operator.getitem, items, self.config)


class ClientNotImplemented(Exception):
    pass


class Notifications(ABC):

    clients = {}

    @classmethod
    def register_client(cls, client):
        def inner_func(calling_cls, *args, **kwargs):
            if client not in cls.clients:
                cls.clients[client] = calling_cls
                logger.debug('Registering new notification client: %s', client)
        return inner_func

    @classmethod
    def factory(cls, client, **kwargs):
        try:
            return cls.clients[client](**kwargs)
        except KeyError:
            raise ClientNotImplemented

    @abstractmethod
    def send_message(self, title: str, message: str):
        pass


@Notifications.register_client('email')
class EmailNotification(Notifications):

    def __init__(self, host: str, login: str, password: str, port: int = 587):
        smtp = smtplib.SMTP(host=host, port=587)
        smtp.starttls()
        smtp.login(login, password)

        self.smtp = smtp

    def send_message(self, from_email: str, to: str, subject: str, body: str):
        msg = MIMEMultipart()

        msg['From'] = from_email
        msg['To'] = to
        msg['Subject'] = subject
        msg['Date'] = formatdate()

        msg.attach(MIMEText(body, 'html', 'utf-8'))
        self.smtp.send_message(msg)


@Notifications.register_client('slack')
class SlackNotification(Notifications):

    def __init__(self, **kwargs):
        self.webhook_url = kwargs['webhook_url']

    def send_message(self, title: str, message: str):
        data = {
            "blocks":
            [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{title}*\n{message}"
                    }
                },
                {
                    "type": "divider"
                }
            ]
        }
        logger.debug(data)
        requests.post(self.webhook_url, json=data)
