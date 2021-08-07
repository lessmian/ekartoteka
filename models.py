from utils import Notifications
from pony.orm import Database, PrimaryKey, Required, Optional, db_session

db = Database()


class DB:

    def __init__(self, filename: str = 'db.sqlite') -> None:

        db.bind(provider='sqlite', filename=filename, create_db=True)
        db.generate_mapping(create_tables=True)


class MessagesModel(db.Entity):
    _table_ = "messages"
    id = PrimaryKey(str, auto=False)
    title = Required(str)
    message = Required(str)
    sent = Optional(int, default=0)


class Message:

    def __init__(self, id: str, title: str, message: str) -> None:
        self.id = id
        self.title = title
        self.message = message

    @db_session
    def add(self) -> None:
        if MessagesModel.get(id=self.id) is None:
            self.m = MessagesModel(
                id=self.id,
                title=self.title,
                message=self.message
            )

    @db_session
    def mark_sent(self) -> None:
        m = MessagesModel.get(id=self.id)
        #m.sent = 1

    @db_session
    def send_notify(self, notifier: Notifications) -> None:

        sent = bool(MessagesModel.get(id=self.id).sent)
        if not sent:
            notifier.send_message(self.title, self.message)
        self.mark_sent()

    @classmethod
    @db_session
    def get_messages(cls):
        return [
            Message(
                id=m.id,
                title=m.title,
                message=m.message
            ) for m in MessagesModel.select()
        ]
