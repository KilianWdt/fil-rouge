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

sensor_id = "capteurTemperature"
start_date = "1"
#start_date = datetime.datetime(2019, 1, 1, 1, 1, 1, 0)
end_date = "200000000000"
#end_date = datetime.datetime.utcnow()

# Requete
results = collection.aggregate(
                            [
                            {"$match": {"SENSOR": sensor_id}},
                            {"$match": {"DATE": {"$gte": start_date}}},
                            {"$match": {"DATE": {"$lte": end_date}}},
                            {"$group": {"_id": "$SENSOR", "moyenne": {"$avg": "$VALUE"}}}
                           ])

# Affichage de la requete
for result in results:
    print(result)
