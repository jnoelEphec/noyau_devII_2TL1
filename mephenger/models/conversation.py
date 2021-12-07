#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient une classe représentant un channel.
    ----- CODE DE LA CLASSE A IMPLEMENTER -----
"""
from typing import Iterable, Optional

from mephenger.exceptions import NoSuchItem, TimeoutExpired
from mephenger.libs import temp_db
from mephenger.models import Model, User

__all__ = ["Conversation"]


class Conversation(Model):
    @staticmethod
    def fetch_by_id(id: int) -> 'Conversation':
        """
        Fetch a `Conversation` from the database.

        # Arguments

        - id: The id of the `Conversation` to fetch.

        # Returns

        The fetched `Conversation`.

        # Errors

        Raises a `TimeoutExpired` exception if the operation takes longer than
        the configured timeout.

        Raises a `NoSuchItem` exception if no conversation with given `id` is
        present in the database.
        """
        try:
            conversations = temp_db.load()["conversations"]
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't fetch conversation {id}")
        if id not in conversations:
            raise NoSuchItem(f"Couldn't fetch conversation {id}")

        members_dict = {name: User.fetch_by_name(name)
                        for name in conversations[id]["members"]}
        owner = None
        name = None
        if len(conversations[id]["members"]) > 2:
            owner = members_dict[conversations[id]["owner"]]
            name = conversations[id]["name"]

        return Conversation(id, members_dict.values(), owner, name)

    def __init__(
        self, id: Optional[int], members: Iterable[User],
        owner: Optional[User] = None, name: Optional[str] = None
    ):
        members = list(members)
        if len(members) > 2 and (owner is None or name is None):
            raise ValueError(
                "Conversations with more than 2 members must have an owner and "
                "a name"
            )
        elif len(members) > 2 and len(name) < 1:
            raise ValueError("Conversations must have a non-empty name")
        elif len(members) < 2:
            raise ValueError("Conversations must have at least 2 members")
        elif owner is not None or name is not None:
            raise ValueError(
                "Conversations with 2 members must not have an owner and "
                "a name"
            )

        self._id = id
        self._members: list[User] = members
        self._owner = owner
        self._name = name

    @property
    def id(self):
        return self._id

    @property
    def members(self):
        return tuple(self.members)

    @property
    def owner(self):
        return self._owner

    @property
    def name(self):
        return self._name

    @property
    def json(self) -> dict:
        return {
            "members": [m.name for m in self.members],
            "owner": self.owner.name,
            "name": self.name,
        }

    def db_push(self):
        def update(db):
            db["conversations"][self.id] = {
                **db["conversation"].get(self.id, {}),
                **self.json,
            }
            return db

        try:
            temp_db.update(update)
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't push conversation {self.id}")

    def db_fetch(self) -> 'Conversation':
        myself = Conversation.fetch_by_id(self.id)
        self._members = myself._members
        self._owner = myself._owner
        self._name = myself._name
        return self
