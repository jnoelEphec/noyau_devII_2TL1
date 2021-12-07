from pymongo import MongoClient

from mephenger import config


class MongoConnector:
    """
        Cette classe permet de créer une connexion vers la base de données.

        Veuillez modifier la variable 'certificat_path' avec le chemin vers
        l'endroit ou se trouve votre certificat.

        Exemple d'utilisation dans votre code :

        try:
            with MongoConnector() as connector:
                collection = connector._db["users"]
                res = collection.find_one()
                print(res)
        except Exception as e:
            print(e)
    """

    def __init__(self):
        client = MongoClient(
            config.DB_URI, tls=True, tlsCertificateKeyFile=config.DB_CERT
        )
        self._db = client['ephecom']

    def __enter__(self) -> 'MongoConnector':
        return self._db

    def __exit__(self):
        self._db.close()
