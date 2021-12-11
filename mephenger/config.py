#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient toutes les variables communes au projet
"""

import os

MAIN_COLOR = (0.580, 0.533, 0.984)
R, G, B, = MAIN_COLOR
BG_COLOR_LEVEL_1 = (R, G, B, 1)
TEXT_COLOR = (1, 1, 1, 1)

DB_CERT = os.environ.get("MEPHENGER_DB_CERT", "mongo-cert.pem")
DB_URI = os.environ.get(
    "MEPHENGER_DB_URI",
    "mongodb+srv://cluster0.5i6qo.gcp.mongodb.net/ephecom-2TL1"
    "?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true"
    "&w=majority&ssl_cert_reqs=CERT_NONE"
)

ROOT_DIR = os.environ.get("PRJ_ROOT", os.getcwd())
PUBLIC_DIR = os.path.join(ROOT_DIR, 'public')
IMG_DIR = os.path.join(PUBLIC_DIR, 'images')
VIEWS_DIR = os.path.join(PUBLIC_DIR, 'views')
TMP_DB_FILE = os.path.join(PUBLIC_DIR, 'tmp_db.json')
