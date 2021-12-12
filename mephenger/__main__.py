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

from mephenger import config, ScreensManager, Session, set_session
from mephenger.db import MongoConnector

Builder.load_file("{0}/common.kv".format(config.VIEWS_DIR))


class Main(App):
    title = 'EpheCom'

    def build(self):
        session = Session(ScreensManager(), "linus", "torvalds")
        set_session(session)
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

    # Ensure we have some dummy user named tux
    # TODO: Remove that once we've got a proper models
    with MongoConnector(config.DB_URI, config.DB_CERT, "ephecom-2TL1") as db:
        db.users.find_one_and_replace(
            {"_id": "linus"},
            {"_id": "linus", "pseudo": "Linus", "password": "torvalds"},
            upsert=True,
        )

    main()
