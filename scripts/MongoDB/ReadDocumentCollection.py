#!/usr/bin/env python

import pymongo
import pprint

from pymongo import MongoClient

# Connexion
client = MongoClient()

# Acces a notre database "client2"
db = client.client2

# Acces a notre collection "ampoule_salleDeBain" au sein de notre database
collection = db.capteurTemperature

result = collection.find_one()
# Affichage de la requete
pprint.pprint(collection.find_one())
