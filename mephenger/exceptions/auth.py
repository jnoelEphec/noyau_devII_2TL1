from mephenger.exceptions.base import MephengerException

__all__ = ["IncorrectPassword", "PermissionDenied"]


class IncorrectPassword(MephengerException):
    @staticmethod
    def code() -> int:
        return 123

    @staticmethod
    def description() -> str:
        return "Incorrect password"


class PermissionDenied(MephengerException):
    @staticmethod
    def code() -> int:
        return 120

    @staticmethod
    def description() -> str:
        return "Permission denied"
