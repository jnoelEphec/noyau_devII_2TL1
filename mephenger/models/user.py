#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient une classe représentant un utilisateur.
    ----- CODE DE LA CLASSE A IMPLEMENTER -----
"""
from typing import Dict, Optional

from mephenger.exceptions import NoSuchItem, TimeoutExpired
from mephenger.libs import temp_db
from mephenger.models.model import Model


class User(Model):
    @staticmethod
    def fetch_by_id(id: str) -> 'User':
        try:
            users = temp_db.load()["users"]
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't fetch user {id}")
        if id not in users:
            raise NoSuchItem(f"Couldn't fetch user {id}")
        return User(id, users[id]["pseudo"])

    def __init__(self, id: str, pseudo: str, password: Optional[str] = None):
        if password is not None and len(password) < 1:
            raise ValueError("User password must be non-empty")
        if len(pseudo) < 1:
            raise ValueError("User pseudo must be non-empty")
        self._id = id
        self._pseudo = pseudo
        self._password = None if password is None else hash(password)

    @property
    def id(self):
        return self._id

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

    def db_push(self):
        def update(db):
            db["users"][self.id] = {
                **db["users"].get(self.id, {}),
                **self.json,
            }
            return db

        try:
            temp_db.update(update)
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't push user {self.id}")

    def db_fetch(self) -> 'User':
        myself = User.fetch_by_id(self.id)
        self._id = myself._id
        return self
