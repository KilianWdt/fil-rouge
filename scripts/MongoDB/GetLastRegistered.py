#!/usr/bin/env python
import pymongo
import pprint

from pymongo import MongoClient

# Connexion
client = MongoClient()

# Acces a notre database "client2"
db = client.client2

# Acces a notre collection "ampoule_salleDeBain" au sein de notre database
collection = db.ampoule_salleDeBain

# Requete
results = collection.aggregate([{"$group": {"_id": "1", "lastRegistered": {"$last": "$date"}}}
])

# Affichage de la requete
for result in results:
     print(result)
