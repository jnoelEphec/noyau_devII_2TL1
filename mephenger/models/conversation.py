#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient une classe représentant un channel.
    ----- CODE DE LA CLASSE A IMPLEMENTER -----
"""
from __future__ import annotations

from typing import Iterable, Optional

from mephenger.exceptions import NoSuchItem, TimeoutExpired, Todo
from mephenger.libs import temp_db
from mephenger.models.model import Model
from mephenger.models.user import User


class Conversation(Model):
    @staticmethod
    def fetch_by_id(_id: str) -> Conversation:
        try:
            conversations = temp_db.load()["conversations"]
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't fetch conversation {_id}")
        if _id not in conversations:
            raise NoSuchItem(f"Couldn't fetch conversation {_id}")

        members_dict = {name: User.fetch_by_id(name)
                        for name in conversations[_id]["members"]}
        owner = None
        name = None
        if len(conversations[_id]["members"]) > 2:
            owner = members_dict[conversations[_id]["owner"]]
            name = conversations[_id]["name"]

        return Conversation(_id, members_dict.values(), owner, name)

    def __init__(
        self, _id: Optional[str], members: Iterable[User],
        owner: Optional[User] = None, name: Optional[str] = None
    ):
        members = list(members)
        if not ((owner is None) ^ (name is None)):
            raise ValueError(
                "Conversation owner and name must be either not specified or "
                "both specified"
            )
        super(Conversation, self).__init__(_id)
        self._members: list[User] = members
        self._owner = owner
        self._name = name

    @property
    def id(self) -> str:
        return self._id

    @property
    def members(self) -> tuple[User]:
        return tuple(self.members)

    @property
    def owner(self) -> User:
        return self._owner

    @property
    def name(self) -> str:
        return self._name

    @property
    def json(self) -> dict:
        return {
            "members": [m.id for m in self.members],
            "owner": self.owner.id,
            "name": self.name,
        }

    def db_push(self):
        def update(db):
            db["conversations"][self.id] = {
                **db["conversation"].get(self.id, {}),
                **self.json,
            }
            return db

        if self.id is None:
            self._id = temp_db.get_id()

        try:
            temp_db.update(update)
            self._up_to_date = True
        except TimeoutExpired:
            raise TimeoutExpired(f"Couldn't push conversation {self.id}")

    def db_fetch(self) -> Conversation:
        myself = Conversation.fetch_by_id(self.id)
        self._members = myself._members
        self._owner = myself._owner
        self._name = myself._name
        self._up_to_date = True
        return self

    def add_member(self, inviter: User, invitee: User):
        """
        Add a `User` to this conversation.

        # Arguments:

        - inviter: The `User` inviting the new user in the group.
        - invitee: the invited `User`.

        # Errors:

        A `PermissionDenied` is raised if `inviter` doesn't have the rights to
        invite `invitee` in the group.
        """
        # Todo
        raise Todo(__file__, Conversation.add_member)
