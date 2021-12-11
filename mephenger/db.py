from __future__ import annotations

from typing import Generator, Optional

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

    def __init__(self, uri: str, cert: str, db_name: Optional[str] = None):
        self._uri = uri
        self._cert = cert
        self._db_name = db_name
        self._db: Optional[Database] = None
        self._conversations: Optional[Collection] = None
        self._messages: Optional[Collection] = None
        self._users: Optional[Collection] = None
        # TODO: Use kivy cache
        self._cache = {"conversations": {}, "messages": {}, "users": {}}

    def __enter__(self) -> MongoConnector:
        self.connect()
        return self

    def __exit__(self):
        self.disconnect()

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def cert(self) -> str:
        return self._cert

    @property
    def conversations(self) -> Collection:
        return self._conversations

    @property
    def messages(self) -> Collection:
        return self._messages

    @property
    def users(self) -> Collection:
        return self._users

    def connect(self):
        """
        Initiate connection to the database.

        A call to this function must be paired with a call to
        `connector.disconnect` before it can be called again.

        This function is automatically called when entering a runtime context.
        """
        client = MongoClient(
            self.uri, tls=True, tlsCertificateKeyFile=self.cert
        )
        if self._db_name is None:
            self._db = client.get_default_database()
        else:
            self._db = client[self._db_name]
        self._conversations: Collection = self._db["conversations"]
        self._messages: Collection = self._db["messages"]
        self._users: Collection = self._db["users"]

    def disconnect(self):
        """
        Tear down connection to the database.

        This function is automatically called when exiting a runtime context.
        """
        self._db.close()
        del self._db
        self._db = None
        self._conversations = None
        self._messages = None
        self._users = None

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
