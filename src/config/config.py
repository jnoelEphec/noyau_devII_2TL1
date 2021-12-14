#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Ce fichier contient toutes les variables communes au projet
"""

# Couleurs
import os
import sys

MAIN_COLOR = (0.580, 0.533, 0.984)
R, G, B, = MAIN_COLOR
BG_COLOR_LEVEL_1 = (R, G, B, 1)
TEXT_COLOR = (1, 1, 1, 1)

# Chemins
ROOT_DIR = sys.path[1]
PUBLIC_DIR = os.path.join(ROOT_DIR, 'public')
IMG_DIR = os.path.join(PUBLIC_DIR, 'images')
VIEWS_DIR = os.path.join(PUBLIC_DIR, 'views')

# Mongodb cert file location
MONGODB_CERT = os.environ.get("MONGODB_CERT", ROOT_DIR + "certif_mongo.pem")
# Mongodb database name
MONGODB_DBNAME = os.environ.get("MONGODB_DBNAME", "ephecom")
# Mongodb database uri
MONGODB_URI = os.environ.get(
    "MONGODB_URI",
    "mongodb+srv://cluster0.5i6qo.gcp.mongodb.net/"
    f"{MONGODB_DBNAME}?authSource=%24external&authMechanism=MONGODB-X509"
    "&retryWrites=true&w=majority&ssl_cert_reqs=CERT_NONE"
)
