#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient une classe représentant un message textuel envoyé
    dans un channel.
    ----- CODE DE LA CLASSE A IMPLEMENTER -----
"""
from __future__ import annotations

from typing import Optional

from mephenger import get_session
from mephenger.exceptions import NoSuchItem
from mephenger.models.conversation import Conversation
from mephenger.models.model import Model
from mephenger.models.user import User


class Message(Model):
    @staticmethod
    def fetch_by_id(_id: str) -> Message:
        message = get_session().db.messages.find_one({"_id": _id})
        if message is None:
            raise NoSuchItem(f"Couldn't fetch message {_id}")
        return Message(**message)

    def __init__(
        self, _id: Optional[str], sender: User, conversation: Conversation,
        text: str
    ):
        super(Message, self).__init__(_id)
        self._sender = sender
        self._conv = conversation
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
        if self.is_in_db:
            assert get_session().db.messages \
                       .update_one({"_id": self.id}, self.json).modified_count \
                   == 1
        else:
            self._id = \
                get_session().db.messages.insert_one(self.json).inserted_id

    def db_fetch(self) -> Message:
        myself = Message.fetch_by_id(self.id)
        self._sender = myself._sender
        self._conv = myself._conv
        self._text = myself._text
        return self
