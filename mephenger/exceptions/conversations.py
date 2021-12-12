from mephenger.exceptions.base import MephengerException

__all__ = ["NotAGroup", "NotAMember"]


class NotAGroup(MephengerException):

    @staticmethod
    def code() -> int:
        return 119

    @staticmethod
    def description() -> str:
        return "Conversation is not a group"


class NotAMember(MephengerException):
    @staticmethod
    def code() -> int:
        return 126

    @staticmethod
    def description() -> str:
        return "User is not a member of the conversation"
