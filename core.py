import requests
from bs4 import BeautifulSoup

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
        self.session.post(f"{url}/index.php", data=payload)

    def rewrite_links(self, message):
        attachements = message.find(id='zalaczniki')
        links = []
        if attachements is not None:
            for a in attachements.findAll('a'):
                href = f"{self.config.get('ekartoteka', 'url')}/{a['href']}"
                text = a.contents[0].replace('\xa0\xa0|\xa0\xa0', '')
                links.append(f'<a href="{href}">{text}</a>')
            message.find(id="zalaczniki").decompose()
            joined_links = " ".join(links)
            return f"{message!r}{joined_links}"
        return f"{message!r}"

    def get_messages(self):
        messages_endpoint = self.config.get('ekartoteka', 'messages_endpoint')
        request = self.session.get(messages_endpoint)
        soup = BeautifulSoup(request.text, features="html.parser")
        titles = soup.find_all("div", {"class": "tytuli arr"})

        for title in titles:
            message_id = title.get('id')[2:]
            message = soup.find(id=f"te{message_id}")
            rewritten_message = self.rewrite_links(message)
            m = Message(message_id, title.text, rewritten_message)
            m.add()

    def send_nofifications(self):
        notifiers = self.config.get('notifiers')

        for name, config, in notifiers.items():
            notifier = Notifications.factory(name, **config)
            messages = Message.get_messages()
            for message in messages:
                message.send_notify(notifier=notifier)
