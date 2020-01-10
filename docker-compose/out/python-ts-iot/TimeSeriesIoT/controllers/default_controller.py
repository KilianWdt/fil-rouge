import connexion
import six
import pymongo
from pymongo import MongoClient
from bson.json_util import dumps
from TimeSeriesIoT import util


def mean_sensor_id_get(sensor_id, start_date=None, end_date=None):  # noqa: E501
    """Calculer la moyenne d&#x27;un capteur entre deux dates

    Optional extended description in CommonMark or HTML. # noqa: E501

    :param sensor_id: String Id of the sensor to get
    :type sensor_id: str
    :param start_date: Integer/timestamp of the start date
    :type start_date: int
    :param end_date: Integer/timestamp of the end date
    :type end_date: int

    :rtype: List[int]
    """

    # Connexion
    client = MongoClient("mongodb://mongo:27017")

    # Acces a notre database "client2"
    db = client.client2

    # Acces a notre collection "capteurTemperature" au sein de notre database
    collection = db.capteurTemperature

    pipeline = [
        {"$match": {"SENSOR": sensor_id}},
        {"$match": {"DATE": {"$gte": start_date}}},
        {"$match": {"DATE": {"$lte": end_date}}},
        {"$group": {"_id": "$SENSOR", "moyenne": {"$avg": "$VALUE"}}}
    ]

    # Requete
    cursor = collection.aggregate(pipeline)

    return cursor["moyenne"]


    #return "Sensor :  " + sensor_id +  " [start:end] : [ " + str(start_date) + ": " + str(end_date) +  "] Valeur moyenne = "
