import threading
from driver.database import BASE, SESSION
from sqlalchemy import Column, String, UnicodeText


class Chats(BASE):
    __tablename__ = "chats"
    chat_id = Column(String(14), primary_key=True)
    chat_name = Column(UnicodeText)

    def __init__(self, chat_id, chat_name=None):
        self.chat_id = chat_id
        self.chat_name = chat_name

Chats.__table__.create(checkfirst=True)

CHATS_LOCK = threading.RLock()
CHATS_DATA = set()

def del_chat(chat_id):
    with CHATS_LOCK:
        chat = SESSION.query(Chats).get(str(chat_id))
        if chat:
            SESSION.delete(chat)
        SESSION.commit()


def chatlists():
    global CHAT_ID
    try:
        CHAT_ID = {int(x.chat_id) for x in SESSION.query(Chats).all()}
        return CHAT_ID
    finally:
        SESSION.close()
