from abc import ABC, abstractmethod

from mephenger.models.conversation import *
from mephenger.models.message import *
from mephenger.models.user import *

__all__ = ["Model"] \
    + conversation.__all__ \
    + message.__all__ \
    + user.__all__


class Model(ABC):
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
        Update the database's state of this object.

        # Errors

        Raises a `TimeoutExpired` exception if the operation takes longer than
        the configured timeout.
        """
        pass

    @abstractmethod
    def db_fetch(self) -> 'Model':
        """
        Update this object's state from the database.

        # Returns

        The updated object.

        # Errors

        Raises a `TimeoutExpired` exception if the operation takes longer than
        the configured timeout.

        Raises a `NoSuchItem` exception if this object is not present in the
        database. You may solve this by calling `db_push()`.
        """
        pass
