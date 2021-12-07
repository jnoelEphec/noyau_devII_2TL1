from __future__ import annotations

from typing import Generator

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from mephenger import models


class MongoConnector:
    """
    Allow connecting to a mongodb database.

    To access the database, use a `with` statement:

    ```
    with MongoConnector(uri, cert) as db:
        my_conv = db.conversations_of_user(my)user)
    ```
    """

    def __init__(self, uri: str, cert: str):
        self._uri = uri
        self._cert = cert
        self._db = None
        # TODO: Use kivy cache
        self._cache = {"conversations": {}, "messages": {}, "users": {}}

    def __enter__(self) -> MongoConnector:
        client = MongoClient(
            self.uri, tls=True, tlsCertificateKeyFile=self.cert
        )
        self._db: Database = client["ephecom"]
        self._conversations: Collection = self._db["conversations"]
        self._messages: Collection = self._db["messages"]
        self._users: Collection = self._db["users"]
        return self

    def __exit__(self):
        self._db.close()
        del self._db
        self._db = None

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def cert(self) -> str:
        return self._cert

    def messages_from_conversation(
        self, conversation: models.Conversation
    ) -> Generator[models.Message]:
        """
        Get an iterator over the messages from given conversation.
        """
        for message in self._messages.find(
                {"conversation": conversation.id}
        ):
            message["conversation"] = conversation
            self._cache["messages"][message["_id"]] = models.Message(**message)
            yield self._cache["messages"][message["_id"]]

    def conversations_of_user(
        self, user: models.User
    ) -> Generator[models.Conversation]:
        """
        Get an iterator over the conversations of a user.
        """
        for conversation in self._conversations.find({"members": user.id}):
            missing_members = [
                u for u in conversation["members"]
                if u not in self._cache["users"]
            ]
            for user in self._users.find({"_id": {"$in": missing_members}}):
                self._cache["users"][user["_id"]] = models.User(**user)
            conversation["members"] = [
                self._cache["users"][u] for u in conversation["members"]
            ]
            self._cache["conversations"][conversation["_id"]] = \
                models.Conversation(**conversation)
            yield self._cache["conversations"][conversation["_id"]]

    # TODO: Implement more methods
