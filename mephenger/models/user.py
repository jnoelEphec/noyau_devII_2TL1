#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient une classe représentant un utilisateur.
    ----- CODE DE LA CLASSE A IMPLEMENTER -----
"""
from __future__ import annotations

from typing import Dict, Optional

from pymongo.errors import PyMongoError

from mephenger import get_session
from mephenger.exceptions import NoSuchItem
from mephenger.models.model import Model


class User(Model):
    backup = {"_id": "linus", "pseudo": "Linus", "password": "torvalds"}

    @staticmethod
    def fetch_by_id(_id: str, password: bool = False) -> User:
        try:
            user = get_session().db.users.find_one({"_id": _id})
        except PyMongoError:
            return User(**User.backup)
        if user is None:
            raise NoSuchItem(f"Couldn't fetch user {_id}")
        if password:
            del user["password"]
        return User(**user)

    def __init__(
        self, _id: str, pseudo: str, password: Optional[str] = None
    ):
        if password is not None and len(password) < 1:
            raise ValueError("User password must be non-empty")
        if len(pseudo) < 1:
            raise ValueError("User pseudo must be non-empty")

        super(User, self).__init__(_id)
        self._pseudo = pseudo
        self._password = None if password is None else password

    @property
    def pseudo(self):
        return self._pseudo

    @property
    def password(self):
        return self._password

    @property
    def json(self) -> Dict:
        json = {
            "_id": self.id,
            "pseudo": self.pseudo,
        }
        if self.password is not None:
            json["password"] = self._password
        return json

    def db_fetch(self) -> User:
        myself = User.fetch_by_id(self.id)
        self._pseudo = myself._pseudo
        if self.password is not None:
            self._password = myself._password
        return self
