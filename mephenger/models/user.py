#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient une classe représentant un utilisateur.
    ----- CODE DE LA CLASSE A IMPLEMENTER -----
"""
from __future__ import annotations

from typing import Dict, Optional

from mephenger import get_session
from mephenger.exceptions import NoSuchItem
from mephenger.models.model import Model


class User(Model):
    @staticmethod
    def fetch_by_id(_id: str, password: bool = False) -> User:
        user = get_session().db.users.find_one({"_id": _id})
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
        self._password = None if password is None else hash(password)
        self._is_in_db = False

    @property
    def pseudo(self):
        return self._pseudo

    @property
    def password(self):
        raise AttributeError("Cannot access user password")

    @password.setter
    def password(self, password: str):
        if password is not None and len(password) < 1:
            raise ValueError("User password must be non-empty")
        self._password = hash(password)

    @property
    def json(self) -> Dict:
        json = {
            "_id": self.id,
            "pseudo": self.pseudo,
        }
        if self.password is not None:
            json["password"] = self._password
        return json

    @property
    def is_in_db(self) -> bool:
        return self._is_in_db

    def db_push(self):
        if self.is_in_db:
            assert get_session().db.users \
                       .update_one({"_id": self.id}, self.json).modified_count \
                   == 1
        else:
            assert get_session().db.users.insert_one(self.json).acknowledged

    def db_fetch(self) -> User:
        myself = User.fetch_by_id(self.id)
        self._pseudo = myself._pseudo
        if self.password is not None:
            self._password = myself._password
        return self
