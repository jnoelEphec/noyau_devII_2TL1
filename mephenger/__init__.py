import json
import os.path

from mephenger import config, exceptions, legacy, models, views
from mephenger.session import Session

__all__ = ["config", "exceptions", "models", "views", "Session"]

# Initialize the temporary database if that's not the case
if not os.path.exists(config.TMP_DB_FILE):
    with open(config.TMP_DB_FILE, "x") as db_file:
        json.dump(
            {
                "messages": {},
                "conversation": {},
                "users": {},
            }, db_file
        )
# Ensure wwe have some dummy user named tux
# TODO: Remove that once we've got a proper models
models.User("tux", "linux").db_push()
