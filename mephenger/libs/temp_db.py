import json
import typing
from copy import deepcopy
from threading import Lock, TIMEOUT_MAX
from typing import Any

from mephenger import config
from mephenger.exceptions import NotJsonSerializable, TimeoutExpired, WouldBlock

DB_MUTEX = Lock()


def load(block: bool = True, timeout: float = TIMEOUT_MAX) -> Any:
    """
    Acquire access to the models and load it.

    If this function acquires exclusive access to the models file, it releases it
    before returning.

    # Arguments

    - block: If set to `False` instead of the default `True`, this call doesn't
    block and returns `id(None)` if it would have blocked if it was set to
    `True`.
    - timeout: The number of seconds to block. The default is the biggest
    allowed value.

    # Returns

    The json representation of the temporary models.

    # Errors

    Raises a `TimeoutExpired` exception if the call blocked for more than
    `timeout` seconds.

    Raises an `OverflowError` if the timeout value is greater than
    `threading.TIMEOUT_MAX`.

    This function doesn't catch any `IOError` or an `OSError` that may be raised
    by function called to read and write the models.
    """
    if not DB_MUTEX.acquire(block, timeout):
        if block:
            raise TimeoutExpired("Couldn't load models")
        raise WouldBlock("Couldn't load models")
    with open(config.TMP_DB_FILE) as db_file:
        db = json.load(db_file)
    DB_MUTEX.release()
    return db


def update(
    updater: typing.Callable[[Any], Any], block: bool = True,
    timeout: float = TIMEOUT_MAX
):
    """
    Acquire exclusive access to the models and update it.

    If this function acquires exclusive access to the models file, it releases it
    before returning.

    # Arguments

    - updater: A function taking the loaded json representation of the temporary
        models, and returning the updated json representation of the temporary models.
        It may mutate the passed object without worries.
    - block: If set to `False` instead of the default `True`, this call doesn't
        block.
    - timeout: The number of seconds to block. The default is the biggest value
        allowed.

    # Errors

    This function raises an `OverflowError` if the timeout value is greater than
    `threading.TIMEOUT_MAX`.

    This function doesn't catch any `IOError` or an `OSError` that may be raised
    by function called to read and write the models.

    If the object returned by `updater` is not json-serializable, raises an
    `NotJsonSerializable` error.
    """
    if not DB_MUTEX.acquire(block, timeout):
        if block:
            raise TimeoutExpired("Couldn't update models")
        raise WouldBlock("Couldn't update models")
    with open(config.TMP_DB_FILE) as db_file:
        db = json.load(db_file)

    try:
        with open(config.TMP_DB_FILE, "w") as db_file:
            json.dump(updater(deepcopy(db)), db_file)
    except TypeError:
        # If the returned object was not JSON-serializable, restore the models and
        # re-raise it
        with open(config.TMP_DB_FILE, "w") as db_file:
            json.dump(db, db_file)
        raise NotJsonSerializable("Couldn't update models")

    DB_MUTEX.release()
