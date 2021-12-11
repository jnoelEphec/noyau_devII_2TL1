#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    [BASE]
    Ce fichier représente une vue contenant la liste des "Team" disponible à
    l'utilisateur.
"""
from typing import Optional

from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManagerException
from kivy.uix.scrollview import ScrollView

from mephenger import config, Session
from mephenger.legacy.models.screens_manager import ScreensManager
from mephenger.models import Conversation

Builder.load_file(f"{config.VIEWS_DIR}/teams.kv")


class TeamsListButton(Button):
    pass


class EmptyTeams(Label):
    pass


class TeamsContainer(ScrollView):

    def __init__(self, session: Session):
        super(TeamsContainer, self).__init__()
        self.content = self.ids.channels_content
        self.sm = ScreensManager()

        self.content.clear_widgets()

        landing_screen = None
        try:
            landing_screen = self.sm.get_screen("landing")
        except ScreenManagerException:
            # FIXME: Handle error, further code has a dependency on
            #  landing_screen
            pass

        def handle(_, conversations: Optional[list[Conversation]] = None):
            if conversations is None:
                conversations = session.conversations
            landing_screen.display_channels(conversations)

        button = TeamsListButton(text="My Team")
        button.bind(on_press=handle)
        self.content.add_widget(button)
