#!/usr/bin/env python
import pymongo
import pprint
import datetime

from pymongo import MongoClient

# Connexion
client = MongoClient()

# Acces a notre database "client2"
db = client.client2

# Acces a notre collection "capteurTemperature" au sein de notre database
collection = db.capteurTemperature

sensor_name = "capteurTemperature"
start_date = datetime.datetime(2019, 1, 1, 1, 1, 1, 0)
end_date = datetime.datetime.utcnow()

# Requete
results = collection.aggregate([{"$match": {"date": {"$gt" : start_date}}},
                                {"$match": {"date": {"$lt" : end_date}}},
                                {"$group": {"_id": "1", "ValeurMinimale": {"$last": "$temperature"}}}
                               ])

# Affichage de la requete
for result in results:
    print(result)
