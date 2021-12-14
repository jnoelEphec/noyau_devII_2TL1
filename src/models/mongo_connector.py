from pymongo import MongoClient

from src.config import config


class MongoConnector:
    """
        Cette classe permet de créer une connexion vers la base de données.

        Veuillez modifier la variable 'certificat_path' avec le chemin vers l'endroit ou se trouve votre certificat.

        Exemple d'utilisation dans votre code :

        try:
            with MongoConnector() as connector:
                collection = connector.db["users"]
                res = collection.find_one()
                print(res)
        except Exception as e:
            print(e)
    """

    def __init__(self):
        client = MongoClient(
            config.MONGODB_URI,
            tls=True,
            tlsCertificateKeyFile=config.MONGODB_CERT,
        )
        self.db = client[config.MONGODB_DBNAME]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.db.close()
