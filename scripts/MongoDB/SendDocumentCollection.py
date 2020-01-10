#!/usr/bin/env python
import pymongo
import datetime

from pymongo import MongoClient

# Connexion
client = MongoClient()

# Creation de la database "client2"
db = client.client2

# Creation de la collection "ampoule_salleDeBain" dans notre database
collection = db.ampoule_salleDeBain

# Creation du document JSON
post = {
"nom": "ampoule_salleDeBain",
"date": datetime.datetime.utcnow(),
"valeur": 0
}

# Envoi du document JSON
post_id = collection.insert_one(post).inserted_id

# Affichage de l'id du document cree par MongoDB
print(post_id)
