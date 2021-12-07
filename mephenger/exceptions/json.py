from mephenger.exceptions.base import MephengerException

__all__ = ["NotJsonSerializable"]


class NotJsonSerializable(MephengerException):
    @staticmethod
    def code() -> int:
        return 125

    @staticmethod
    def description() -> str:
        return "Not JSON-serializable"
