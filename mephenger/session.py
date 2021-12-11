from __future__ import annotations

from hmac import compare_digest
from typing import Optional

from mephenger import ScreensManager
from mephenger.db import MongoConnector
from mephenger.exceptions import IncorrectPassword, NotAMember
from mephenger.models import Conversation, User
from mephenger.views import LandingScreen


class Session:

    def __init__(
        self, screens_manager: ScreensManager, connector: MongoConnector,
        login: str, password: str
    ):
        user = User.fetch_by_id(login, password=True)
        # TODO: Use a stronger hash than python's builtin
        if not compare_digest(hash(password), user.password):
            raise IncorrectPassword(f"Couldn't log user {user} in")
        self._screens_manager = screens_manager
        self._connector = connector
        self._user = user
        self._conversations: dict[int, Conversation] = {}
        self._current_conversation: Optional[int] = None
        self._landing_screen = LandingScreen(self)
        screens_manager.add_widget(self._landing_screen)
        screens_manager.current = "landing"
        self._landing_screen.set_teams_list()

    def __del__(self):
        # used to log off
        pass

    @property
    def screens_manager(self):
        return self._screens_manager

    @property
    def connector(self):
        return self._connector

    @property
    def landing_screen(self):
        return self._landing_screen

    @property
    def user(self) -> User:
        return self._user

    @property
    def conversations(self) -> list[Conversation]:
        return list(self._conversations.values())

    @property
    def current_conversation(self) -> Conversation:
        return None if self._conversations is None \
            else self._conversations[self._current_conversation]

    @current_conversation.setter
    def current_conversation(self, conv: Conversation):
        if conv.id in self._conversations:
            raise NotAMember("Cannot switch to conversation")
        self._current_conversation = conv.id

    @current_conversation.deleter
    def current_conversation(self):
        self._current_conversation = None

    def create_group(self, name: str) -> Conversation:
        """
        Create a new `Group`. The currently logged in user will be the owner and
        the only member upon creation.

        # Arguments

        - name: The group's name.

        # Return

        The newly created group
        """
        return Conversation(None, (self.user,), self.user, name)

    def add_to_group(self, group: Conversation, user: User):
        """
        Add a `User` to a `Group`.

        # Arguments

        - group: The `Group` to add a user to.
        - user: The `User` to add in the `Group`.

        # Errors

        Raises a `PermissionDenied` exception if the logged in user doesn't
        have enough privilege to add `user` to `group`.
        """
        group.add_member(self._user, user)
