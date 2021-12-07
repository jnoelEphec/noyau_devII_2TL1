from abc import ABC, abstractmethod


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
