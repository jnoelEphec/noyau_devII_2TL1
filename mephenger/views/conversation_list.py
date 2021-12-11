#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    [BASE]
    Ce fichier représente la liste des 'Channel' disponibles pour l'utilisateur.
"""
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView

from mephenger import config, get_session
from mephenger.models import Conversation

Builder.load_file(f"{config.VIEWS_DIR}/channel.kv")


class ConversationTitleRow(BoxLayout):
    pass


class ConversationLabel(Label):
    pass


class ConversationAddButton(Button):
    pass


class ConversationsListButton(Button):
    pass


class ConversationsContainer(ScrollView):

    def __init__(self, conversations: list[Conversation]):
        super(ConversationsContainer, self).__init__()
        self.conversations = conversations
        self.channels_container = self.ids.channels_content

        pms_group = self.init_group("Private Messages")
        groups_group = self.init_group("Groups")
        self.channels_container.add_widget(pms_group)
        self.channels_container.add_widget(groups_group)

        def handle(_, _id: str):
            get_session().landing_screen.display_conversation(_id)

        for conversation in self.conversations:
            conversation_row = ConversationsListButton(
                text=conversation.name, on_press=handle
            )
            if conversation.is_group:
                groups_group.add_widget(conversation_row)
            else:
                pms_group.add_widget(conversation_row)

    def init_group(self, group: str):
        def handle(_, name: str = group):
            self.add_new_conversation(name)

        group_box = BoxLayout(orientation="vertical", size_hint_y=None)
        title_row = ConversationTitleRow()
        title_label = ConversationLabel(text=group)
        title_add_btn = ConversationAddButton(on_press=handle)
        title_row.add_widget(title_label)
        title_row.add_widget(title_add_btn)
        group_box.add_widget(title_row)
        return group_box

    def add_new_conversation(self, group_name):
        """
        Cette méthode permet d'ajouter un nouveau channel dans le groupe
        concerné.
        :param group_name: Représente le nom du groupe concerné.
        """
        content = RelativeLayout()

        content.add_widget(
            Label(text="Le nom du nouveau channel et d'autres éléments")
        )
        content.add_widget(
            Button(
                text="Ajouter", size_hint=(None, None), size=(150, 40),
                pos_hint={'center_x': .4, 'center_y': .1}
            )
        )
        cancel = Button(
            text="Annuler", size_hint=(None, None), size=(150, 40),
            pos_hint={'center_x': .6, 'center_y': .1}
        )
        content.add_widget(cancel)

        popup = Popup(
            title="Ajouter un nouveau channel à {0}".format(group_name),
            size_hint=(.5, .5),
            pos_hint={'center_x': .5, 'center_y': .5},
            content=content,
            auto_dismiss=False
        )

        cancel.bind(on_press=lambda a: popup.dismiss())

        popup.open()
