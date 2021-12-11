from __future__ import annotations

from hmac import compare_digest
from typing import Optional

from mephenger import Conversation, Group, models, User
from mephenger.exceptions import IncorrectPassword, NotAMember


class Session:

    @staticmethod
    def log_in(login: str, password: str) -> Session:
        user = models.User.fetch_by_id(login, password=True)
        # TODO: Use a stronger hash than python's builtin
        if compare_digest(hash(password), user.password):
            return Session(user)
        raise IncorrectPassword(f"Couldn't log user {user.id} in")

    def __init__(self, user: User):
        self._user = user
        self._conversations: dict[int, Conversation] = {}
        self._current_conversation: Optional[int] = None

    @property
    def user(self):
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
