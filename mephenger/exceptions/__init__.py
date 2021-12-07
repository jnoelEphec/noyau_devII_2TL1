from abc import ABC, abstractmethod

from mephenger.exceptions.auth import *
from mephenger.exceptions.concurrency import *
from mephenger.exceptions.json import *

__all__ = ["MephengerException", "NotAMember", "NoSuchItem"] \
          + auth.__all__ \
          + concurrency.__all__ \
          + json.__all__


class MephengerException(ABC, Exception):
    @staticmethod
    @abstractmethod
    def code() -> int:
        """
        The unique code of this class of exception. If a process encounters a
        MephengerException and cannot handle it, it should exit with with a
        status equal to this code.

        It should be between 0 and 128 (both exclusive).
        """
        pass

    @staticmethod
    @abstractmethod
    def description() -> str:
        """
        A short one line description of this error class.
        """

    def __init__(self, msg: str = ""):
        super(MephengerException, self).__init__(msg)
        self._msg = msg

    def __repr__(self):
        return f"{self.__class__.__name__} ({hex(self.code())}) {self._msg}: " \
               f"{self.description()}"


class NoSuchItem(MephengerException):
    @staticmethod
    def code() -> int:
        return 127

    @staticmethod
    def description() -> str:
        return "No such item"


class IncompleteItem(MephengerException):
    @staticmethod
    def code() -> int:
        return 122

    @staticmethod
    def description() -> str:
        return "Item is incomplete"
