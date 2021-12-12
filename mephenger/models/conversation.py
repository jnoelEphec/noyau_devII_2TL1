#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient une classe représentant un channel.
    ----- CODE DE LA CLASSE A IMPLEMENTER -----
"""
from __future__ import annotations

from typing import Iterable, Optional

from mephenger import get_session
from mephenger.exceptions import (
    NoSuchItem,
    NotAGroup,
    PermissionDenied,
)
from mephenger.models.model import Model
from mephenger.models.user import User


class Conversation(Model):
    @staticmethod
    def fetch_by_id(_id: str) -> Conversation:
        conversation = get_session().db.conversations.find_one({"_id": _id})
        if conversation is None:
            raise NoSuchItem(f"Couldn't fetch conversation {_id}")
        return Conversation(**conversation)

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

    @property
    def is_group(self):
        return self.owner is not None and self.name is not None

    def db_fetch(self) -> Conversation:
        myself = Conversation.fetch_by_id(self.id)
        self._members = myself._members
        self._owner = myself._owner
        self._name = myself._name
        return self

    def add_member(self, inviter: User, invitee: User):
        """
        Add a `User` to this conversation.

        # Arguments:

        - inviter: The `User` inviting the new user in the group.
        - invitee: the invited `User`.

        # Errors:

        A `NotAGroup` exception is raised if this `Conversation` is not a group.

        A `PermissionDenied` is raised if `inviter` doesn't have the rights to
        invite `invitee` in the group.
        """
        if not self.is_group:
            raise NotAGroup(
                f"User {inviter} cannot invite user {invitee} in group {self}"
            )
        if inviter.id != self.owner.id:
            raise PermissionDenied(
                f"User {inviter} cannot invite user {invitee} in group {self}"
            )
        self._members.append(invitee)
