from abc import ABC

from mephenger import models


class Conversation(ABC):
    def __init__(self, model: models.Conversation):
        self._model = model

    @property
    def id(self):
        return self._model.id
