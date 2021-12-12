#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient une classe représentant un message textuel envoyé
    dans un channel.
    ----- CODE DE LA CLASSE A IMPLEMENTER -----
"""
from __future__ import annotations

from typing import Optional

from pymongo.errors import PyMongoError

from mephenger import get_session
from mephenger.exceptions import NoSuchItem
from mephenger.models.conversation import Conversation
from mephenger.models.model import Model
from mephenger.models.user import User


class Message(Model):
    backup = {
        "_id": "314159265358979",
        "sender": User(**User.backup),
        "conversation": Conversation(**Conversation.backup),
        "text": "Okay. I got an idea guys. I'm gonna re-implement Unix from "
                "scratch - without all the GNU crap - and I'm gonna call it... "
                "BSD."
    }

    @staticmethod
    def fetch_by_id(_id: str) -> Message:
        try:
            message = get_session().db.messages.find_one({"_id": _id})
        except PyMongoError:
            return Message(**Message.backup)
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

    def db_fetch(self) -> Message:
        myself = Message.fetch_by_id(self.id)
        self._sender = myself._sender
        self._conv = myself._conv
        self._text = myself._text
        return self
