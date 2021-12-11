#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Projet EpheCom
    ===================================

    Ce logiciel a été développé dans le cadre scolaire.
    EpheCom est un logiciel de communications - vocale et écrite - en temps
    réel.
    Il a pour but d'améliorer la communication au sein de l'établissement
    scolaire.

    Version de Python : 3.9
    Système d'exploitation : Windows, OSX, Linux
    Type : Application de bureau
    Language utilisé pour coder : Anglais
    Language utilisé pour documenter : Français
    Documentation Framework : https://kivy.org/doc/stable/api-kivy.html
    Source unique des icons : https://remixicon.com/

    Convention de nommage :
        https://www.python.org/dev/peps/pep-0008/

"""

from dotenv import load_dotenv
from kivy.app import App
from kivy.lang import Builder

from mephenger import config, ScreensManager, Session
from mephenger.db import MongoConnector

Builder.load_file("{0}/common.kv".format(config.VIEWS_DIR))


class Main(App):
    title = 'EpheCom'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._connector = MongoConnector(
            config.DB_URI, config.DB_CERT, "ephecom-2TL1"
        ).__enter__()

    def __del__(self):
        self._connector.__exit__()

    def build(self):
        session = Session(
            ScreensManager(), self._connector, "linus", "torvalds"
        )
        return session.screens_manager


class Personne:
    def __init__(self, nom):
        self.nom = nom


class Etudiant(Personne):
    def __init__(self, nom):
        super(Etudiant, self).__init__(nom)


def main():
    print("Bienvenue sur notre projet commun !")

    Main().run()


if __name__ == '__main__':
    load_dotenv()

    main()
