from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


class Model(ABC):
    @staticmethod
    @abstractmethod
    def fetch_by_id(_id: str) -> Model:
        """
        Fetch a `Model` from the database.

        # Arguments

        - _id: The id of the `Model` to fetch.

        # Returns

        The fetched `Model`.

        # Errors

        Raises a `TimeoutExpired` exception if the operation takes longer than
        the configured timeout.

        Raises a `NoSuchItem` exception if no `Model` with given `id` is present
        in the database.
        """
        pass

    def __init__(self, _id: Optional[str]):
        self._id = _id
        self._up_to_date = _id is not None

    def __setattr__(self, key, value):
        super(Model, self).__setattr__(key, value)
        if key is "_up_to_date":
            return
        self._up_to_date = False

    @property
    def id(self) -> Optional[str]:
        """
        The unique identifier of this message, if it has one.
        """
        return self._id

    @property
    def up_to_date(self) -> bool:
        """
        Check whether the database is up-to-date with the model's state.
        """
        return self._up_to_date

    @property
    @abstractmethod
    def json(self) -> dict:
        """
        Get the json representation of this object.
        """
        pass

    @abstractmethod
    def db_push(self):
        """
        Update the database's state of this object. If this model wasn't in the
        database yet (i.e. it's `id` was still None), update its `_id`.

        The model must set its `_up_to_date` member to `True` if and only if
        the operation is successful.

        # Errors

        Raises a `TimeoutExpired` exception if the operation takes longer than
        the configured timeout.
        """
        pass

    @abstractmethod
    def db_fetch(self) -> Model:
        """
        Update this object's state from the database.

        The model must set its `_up_to_date` member to `True` if and only if
        the operation is successful.

        # Returns

        The updated object.

        # Errors

        Raises a `TimeoutExpired` exception if the operation takes longer than
        the configured timeout.

        Raises a `NoSuchItem` exception if this object is not present in the
        database. You may solve this by calling `db_push()`.
        """
        pass

    def is_in_db(self) -> bool:
        """
        Check if the model is present in the database.

        # Returns

        `True` if the model has been assigned an id, `False` otherwise.
        """
        return self.id is not None
