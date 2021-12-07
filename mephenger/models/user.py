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
    def fetch_by_name(name: str):
        """
        Fetch an `User` from the database.

        # Arguments

        - name: The name of the `Message` to fetch.

        # Returns

        The fetched `User`.

        # Errors

        Raises a `TimeoutExpired` exception if the operation takes longer than
        the configured timeout.

        Raises a `NoSuchItem` exception if no user with given `name` is present
        in the database.
        """
        try:
            users = temp_db.load()["users"]
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't fetch user {name}")
        if name not in users:
            raise NoSuchItem(f"Couldn't fetch user {name}")
        return User(name)

    def __init__(self, name: str, password: Optional[str] = None):
        if password is not None and len(password) < 1:
            raise ValueError("User password must be non-empty")
        self._name = name
        self._password = None if password is None else hash(password)

    @property
    def name(self):
        return self._name

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
        if self._password is None:
            return {}
        return {
            "password": self._password,
        }

    def db_push(self):
        def update(db):
            db["users"][self.name] = {
                **db["users"].get(self.name, {}),
                **self.json,
            }
            return db

        try:
            temp_db.update(update)
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't push user {self.name}")

    def db_fetch(self) -> 'User':
        myself = User.fetch_by_name(self.name)
        self._name = myself._name
        return self
