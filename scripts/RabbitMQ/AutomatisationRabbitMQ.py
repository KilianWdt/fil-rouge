#!/usr/bin/env python
import pika
from os import system

credentials = credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
nomClient = ""
nomPiece = ""
nomObjet = ""
listeObjets = []
listePieces = []


def ajouterClient(nomClient, listeObjets, listePieces):

    # Creation Virtual Host client avec API REST
    system('curl -u rabbitmq:rabbitmq -X PUT http://localhost:15672/api/vhosts/' + nomClient)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost', 5672, nomClient, credentials))
    channel = connection.channel()

    # Creation des 3 exchanges
    channel.exchange_declare(exchange="Master", exchange_type="fanout")
    channel.exchange_declare(exchange="Selection Piece", exchange_type="topic")
    channel.exchange_declare(exchange="Selection Objet", exchange_type="topic")

    # Creation de la queue "Maison"
    channel.queue_declare(queue="Maison")

    # Binding des 3 exchanges et de la queue "Maison"
    channel.exchange_bind(destination="Selection Piece", source="Master")
    channel.exchange_bind(destination="Selection Objet", source="Master")
    channel.queue_bind(exchange="Master", queue="Maison")

    # Creation et Binding des queues pour chaque piece
    for piece in listePieces:
        channel.queue_declare(queue=piece)
        channel.queue_bind(exchange="Selection Piece",
                           queue=piece, routing_key=piece + ".*")

    # Creation et Binding des queues pour chaque objet
    for objet in listeObjets:
        channel.queue_declare(queue=objet)
        channel.queue_bind(exchange="Selection Objet",
                           queue=objet, routing_key="*." + objet)


def ajouterUnObjet():
    flag = True

    while flag:
        print("Nom de l'objet : ")
        nomObjet = input()
        listeObjets.append(nomObjet)
        response = ""

        while response != "y" and response != "n":
            print(nomClient + " a-t-il d'autres objets ? [y/n]")
            response = input()
            if response == "y":
                flag = True
            elif response == "n":
                flag = False


def ajouterUnePiece():
    for objet in listeObjets:
        print("Dans quelle piece se trouve " + objet + " ? : ")
        nomPiece = input()
        listePieces.append(nomPiece)

# --------------------------------------------------------------------------------------------

# PENSEZ A METTRE DES "" DANS LES INPUTS


print("")
print("Bienvenue dans l'utilitaire d'ajout client dans votre serveur Rabbitmq (localhost).")
print("-----------------------------------------------------------------------------------")
print("")

print("Renseignez le nom du client : ")
nomClient = input()

ajouterUnObjet()
ajouterUnePiece()

print("------------------------------------------------------------------------------------")
print("Architecture OK")
print("")

ajouterClient(nomClient, listeObjets, listePieces)
