from mephenger.exceptions import MephengerException

__all__ = ["NotAMember", "IncorrectPassword"]


class NotAMember(MephengerException):
    @staticmethod
    def code() -> int:
        return 126

    @staticmethod
    def description() -> str:
        return "User is not a member of the conversation"


class IncorrectPassword(MephengerException):
    @staticmethod
    def code() -> int:
        return 123

    @staticmethod
    def description() -> str:
        return "Incorrect password"
