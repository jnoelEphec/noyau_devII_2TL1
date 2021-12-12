from __future__ import annotations
from typing import Optional


def get_session() -> Optional[Session]:
    return __CURRENT_SESSION


def set_session(s: Session):
    global __CURRENT_SESSION
    __CURRENT_SESSION = s


from mephenger import config, exceptions, legacy, models, views
from mephenger.screens_manager import ScreensManager
from mephenger.session import Session

__all__ = ["config", "exceptions", "models", "views", "get_session",
           "ScreensManager", "set_session", "Session"]

__CURRENT_SESSION = None
