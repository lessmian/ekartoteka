import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

from utils import Config, Notifications
from models import DB, Message


class Ekartoteka:

    def __init__(self, config: Config) -> None:
        self.config = config
        self.session = requests.Session()
        DB()

    def login(self):

        payload = {
            "wlo": self.config.get('ekartoteka', 'login'),
            "ha": self.config.get('ekartoteka', 'password')
        }
        url = self.config.get('ekartoteka', 'url')
        self.session.post(url, data=payload)

    def get_messages(self):
        messages_endpoint = self.config.get('ekartoteka', 'messages_endpoint')
        request = self.session.get(messages_endpoint)
        soup = BeautifulSoup(request.text, features="html.parser")
        titles = soup.find_all("div", {"class": "tytuli arr"})

        for title in titles:
            message_id = title.get('id')[2:]
            message = soup.find(id=f"te{message_id}")
            markdown_message = markdownify(f'{message!r}')
            m = Message(message_id, title.text, markdown_message)
            m.add()

    def send_nofifications(self):
        notifiers = self.config.get('notifiers')

        for name, config, in notifiers.items():
            notifier = Notifications.factory(name, **config)
            messages = Message.get_messages()
            for message in messages:
                message.send_notify(notifier=notifier)
