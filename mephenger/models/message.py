#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient une classe représentant un message textuel envoyé
    dans un channel.
    ----- CODE DE LA CLASSE A IMPLEMENTER -----
"""
from __future__ import annotations

from typing import Optional

from mephenger.exceptions import NoSuchItem, TimeoutExpired
from mephenger.libs import temp_db
from mephenger.models.conversation import Conversation
from mephenger.models.model import Model
from mephenger.models.user import User


class Message(Model):
    @staticmethod
    def fetch_by_id(_id: str) -> Message:
        try:
            messages = temp_db.load()["messages"]
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't fetch message {_id}")
        if _id not in messages:
            raise NoSuchItem(f"Couldn't fetch message {_id}")

        return Message(
            _id,
            User.fetch_by_id(messages[_id]["sender"]),
            Conversation.fetch_by_id(messages[_id]["conversation"]),
            messages[_id]["text"]
        )

    def __init__(
        self, _id: Optional[str], sender: User, conv: Conversation, text: str
    ):
        super(Message, self).__init__(_id)
        self._sender = sender
        self._conv = conv
        self._text = text

    @property
    def sender(self) -> User:
        """
        The user that sent this message.
        """
        return self._sender

    @property
    def conversation(self) -> Conversation:
        return self._conv

    @property
    def text(self) -> str:
        """
        The message's text content.
        """
        return self._text

    @text.setter
    def text(self, text: str):
        # FIXME: do we need escaping / checks ?
        self._text = text

    @property
    def json(self) -> dict:
        return {
            "sender": self.sender.id,
            "conversation": self.conversation.id,
            "text": self.text,
        }

    def db_push(self):
        def update(db):
            db["messages"][self.id] = {
                **db["messages"].get(self.id, {}),
                **self.json,
            }
            return db

        try:
            temp_db.update(update)
            self._up_to_date = True
            if self.id is None:
                self._id = temp_db.get_id()
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't push message {self.id}")

    def db_fetch(self) -> Message:
        myself = Message.fetch_by_id(self.id)
        self._sender = myself._sender
        self._text = myself._text
        self._up_to_date = True
        return self
