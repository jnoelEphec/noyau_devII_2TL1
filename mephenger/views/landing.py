#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    [BASE]
    Ce fichier représente l'interface de lancement de l'application.
    Cette interface contient 3 zones distinctes :
        - Le header de notre application
        - La liste de nos différents channels/groupes
        - La zone de contenu de nos channels après sélection d'un channel.
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from mephenger import config
from mephenger.legacy.models.screens_manager import ScreensManager
from mephenger.views.conversation_list import ConversationsContainer
from mephenger.views.conversation import Conversation
from mephenger.views.teams_container import TeamsContainer

Builder.load_file(f"{config.VIEWS_DIR}/header.kv")
Builder.load_file(f"{config.VIEWS_DIR}/landing.kv")


class LandingScreen(Screen):
    def __init__(self):
        super(LandingScreen, self).__init__()
        self.name = "landing"
        self.sm = ScreensManager()
        self.conv_box = self.ids.conversation_box
        self.rooms_box = self.ids.rooms_box
        self.channels_container = None

    def redirect_to_href(self, href: str):
        """
            [Base]
            Gestion des évènements de redirection du Screen.
            :param href: Le nom du Screen vers lequel naviguer.
        """
        self.sm.redirect(href)

    def display_channels(self, team_channels: list):
        """
            [Base]
            Permet la mise à jour de la liste des "Channel" après un clic sur
            le nom d'une "Team".
            :param team_channels: Liste des 'Channel' de la "Team" concernée.
        """
        self.conv_box.clear_widgets()
        self.rooms_box.clear_widgets()
        self.rooms_box.add_widget(ConversationsContainer(team_channels))

    def display_conversation(self, channel_id: str):
        """
            [Base]
            Permet la mise à jour de la conversation active après un clic sur
            le nom d'un "Channel".
            :param channel_id: L'identifiant du "Channel" concerné sur 8
            caractères.
        """
        self.conv_box.clear_widgets()
        conversation = Conversation(channel_id)
        self.conv_box.add_widget(conversation)

    def set_teams_list(self):
        """
            [Base]
            Initialise la liste des "Team" dont l'utilisateur fait partie.
        """
        self.channels_container = TeamsContainer()
        self.ids.channels_box.add_widget(self.channels_container)
