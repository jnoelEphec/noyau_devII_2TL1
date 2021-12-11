#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient une classe représentant un utilisateur.
    ----- CODE DE LA CLASSE A IMPLEMENTER -----
"""
from __future__ import annotations

from typing import Dict, Optional

from mephenger.exceptions import NoSuchItem, TimeoutExpired
from mephenger.libs import temp_db
from mephenger.models.model import Model


class User(Model):
    @staticmethod
    def fetch_by_id(_id: str, password: bool = False) -> User:
        try:
            users = temp_db.load()["users"]
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't fetch user {_id}")
        if _id not in users:
            raise NoSuchItem(f"Couldn't fetch user {_id}")
        if password:
            user = User(_id, users[_id]["pseudo"], users[_id]["password"])
        else:
            user = User(_id, users[_id]["pseudo"])
        user._is_in_db = True
        user._up_to_date = True
        return user

    def __init__(
        self, _id: Optional[str], pseudo: str, password: Optional[str] = None
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
            "pseudo": self.pseudo
        }
        if self._password is not None:
            json["password"] = self._password
        return json

    @property
    def is_in_db(self) -> bool:
        return self._is_in_db

    def db_push(self):
        def update(db):
            db["users"][self.id] = {
                **db["users"].get(self.id, {}),
                **self.json,
            }
            return db

        try:
            temp_db.update(update)
            self._is_in_db = True
            self._up_to_date = True
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't push user {self.id}")

    def db_fetch(self) -> User:
        myself = User.fetch_by_id(self.id)
        self._id = myself._id
        self._is_in_db = True
        self._up_to_date = True
        return self
