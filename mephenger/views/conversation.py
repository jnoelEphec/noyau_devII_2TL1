#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    [BASE]
    Ce fichier représente une zone de conversation.
"""
from typing import Literal

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView

from mephenger import config, models, Session
from mephenger.db import MongoConnector
from mephenger.libs.bot.commands import Commands
from mephenger.models import Message, User

Builder.load_file(f"{config.VIEWS_DIR}/conversation.kv")


class InputsContainer(BoxLayout):
    pass


class MessageLabel(Label):
    pass


class MessageSent(MessageLabel):
    pass


class MessageReceived(MessageLabel):
    pass


class ConversationContainer(ScrollView):

    def __init__(self, conversation: models.Conversation):
        super(ConversationContainer, self).__init__()
        self._conversation = conversation
        self.messages_box = self.ids.messages_container

        # Démarrer la mise à jour régulière de la conversation
        self.constant_update()

    def constant_update(self):
        self.init_conversation()
        # time.sleep(1)

    def init_conversation(self):
        with MongoConnector(config.DB_URI, config.DB_CERT) as db:
            for msg in db.messages_from_conversation(self._conversation):
                self.messages_box.add_widget(
                    # TODO: Add datetime in messages
                    MessageSent(
                        text=f"1970/01/01 00:00 - {msg.sender}\n{msg.text}"
                    ),
                    len(self.messages_box.children)
                )

    def add_message(
        self, msg_obj: Message, pos: Literal["left", "right"] = "left"
    ):
        msg = MessageSent()
        if pos == "right":
            msg = MessageReceived()

        msg.text = f"1970/01/01 00:00 - {msg_obj.sender}\n{msg_obj.text}"
        self.messages_box.add_widget(msg, len(self.messages_box.children))


class Conversation(RelativeLayout):
    def __init__(self, model: models.Conversation):
        super(Conversation, self).__init__()
        self.messages_container = ConversationContainer(model)
        self.inputs_container = InputsContainer()

        self.add_widget(self.messages_container)
        self.add_widget(self.inputs_container)

    def send_message(self, session: Session):
        txt = self.inputs_container.ids.message_input.text

        if txt:
            msg = Message(None, session.user, self._conversation, txt)
            self.messages_container.add_message(msg)
            msg.db_push()

            if txt[0] == "/":
                bot = Commands(txt)
                response_from_bot = bot.result
                msg_res = Message(
                    None, User("e-bot", "e-bot", None), self._conversation,
                    response_from_bot,
                )
                self.messages_container.add_message(msg_res, pos="right")

            self.inputs_container.ids.message_input.text = ""
