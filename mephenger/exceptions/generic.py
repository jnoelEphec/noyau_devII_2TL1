from mephenger.exceptions.base import MephengerException


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
