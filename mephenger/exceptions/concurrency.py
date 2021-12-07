from mephenger.exceptions.base import MephengerException

__all__ = ["TimeoutExpired", "WouldBlock"]


class TimeoutExpired(MephengerException):
    @staticmethod
    def code() -> int:
        return 124

    @staticmethod
    def description() -> str:
        return "Timeout expired"


class WouldBlock(MephengerException):
    @staticmethod
    def code() -> int:
        return 123

    @staticmethod
    def description() -> str:
        return "Would block"
