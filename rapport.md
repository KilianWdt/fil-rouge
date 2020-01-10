
# Rapport - Fil Rouge

Génération message automatique dans bon virtual host rabbitmq
TP1
Redescente d'information à demander à Pierre Courbin.
TP1
Index TP2

> Kilian Weydert
12 janvier 2020
*Développement d'applications et webservices pour l'IoT*

## Introduction

Ce document est un rapport sur le travail fourni lors des différents TPs.
Le contexte est le suivant :
- Nous sommes une entreprise qui propose de rassembler les données issues d’objets domotiques/énergétiques afin de proposer des dashboards de suivi à nos clients. Nous pensons que plus on connait et on visualise ses propres données, plus on est en enclin à faire attention à sa consommation notamment. Nous voulons ainsi apporter notre solution pour tenter d’aider les gens à être plus sobres énergétiquement ;
- Nous avons déjà 2 clients ([Annexe A.1](#AnnexeA1), [Annexe A.2](#AnnexeA2)) ;
- Nous avons déjà bien avancé sur une première structuration des différentes informations récupérable ([Annexe B](#AnnexeB)) ;
- Nous ne produisons pas de capteurs ou d’actionneurs. Nous nous appuyons sur un réseau de partenaires qui nous permettent de récupérer les données de nos clients sans avoir à installer quoi que ce soit chez lui.

# Table des matières

1. [Ingestion](#Ingestion)
2. [Stockage](#Stockage)
3. [Data Routing](#DataRouting)
4. [Visualisation](#Visualisation)
5. [API](#API)

## Ingestion des données <a id="Ingestion"></a>

Technologie utilisée : __RabbitMQ__

1. [Définition de l'architecture](#DéfinitionArchitecture)
2. [Déploiement de l'architecture](#DéploiementArchitecture)
3. [Découvrir la réception et l'envoi de messages](#RéceptionEnvoiMessages)
4. [Automatisation du déploiement](#AutomatisationDéploiement)
5. [Génération automatique de messages](#GénérationAutomatique)

### Définition de l'architecture <a id="DéfinitionArchitecture"></a>

L'ingestion des données consiste en la récupération des données envoyées par l'ensemble des objets connectés. Nous allons trier les données dès l'ingestion afin d'obtenir des *queues* pour chaque :
* Client
* Pièce du client
* Objet du client

 Une telle architecture nous permet de faciliter le futur *stockage* et *traitements* des données.

Chaque client aura son propre serveur virtuel pour une meilleure séparation des données.
<a id="ArchitectureRabbitMQ"></a>

<img src="Images/ArchitectureIngestion.png" alt="Architecture Ingestion" width="500"/>

Pour chaque chaque client, on crée :
* Un host virtuel ;
* Un exchange _Master_ connecté à une queue _Maison_ ainsi qu'à un exchange _selectionPiece_ et _selectionObjet_ ;
* Un exchange _Selection Piece_ chargé de distribuer le message dans la queue correspondant à celle de la pièce ;
* Un exchange _Selection Objet_ chargé de distribuer le message dans la queue correspondant à celle de l'objet.
* Les objets utiliseront la routing key : _nomPiece.nomObjet_

### Déploiement de l'architecture <a id="DéploiementArchitecture"></a>

_docker-compose.yml_ permettant de déployer un serveur RabbitMQ :
```yml
version: '3.7'
services:

    rabbitmq:
        image: "rabbitmq:3-management"
        hostname: "rabbitmq"
        environment:
            RABBITMQ_ERLANG_COOKIE: "SWQOKODSQALRPCLNMEQG"
            RABBITMQ_DEFAULT_USER: "rabbitmq"
            RABBITMQ_DEFAULT_PASS: "rabbitmq"
            RABBITMQ_DEFAULT_VHOST: "/"
        ports:
            - "15672:15672"
            - "5672:5672"
        networks:
            - iot-labs
        labels:
            NAME: "rabbitmq"

networks:
    iot-labs:
        external: true
```

Nous allons implémenter l'architecture nécessaire pour notre [Client 2](#AnnexeB).
C'est à dire que nous allons créer :
- Les exchanges : _Master_, _Selection Piece_, _Selection Objet_
- Les queues :
	* _Maison_
	* _Piece Principale_ ; _Salle de Bain_
	* _ampoule_principale_ ; _detecteurPresence_principale_ ; _capteurTemperature_principale_ ; _radiateur_principale_ ; _capteurPuissanceBallonEau_ ; _radiateur_salleDeBain_ ; _ampoule_salleDeBain_.
- Les bindings (_comme sur le schéma [ici](#ArchitectureRabbitMQ)_)

<img src="Images/Exchanges.png" alt="Exchanges" width="500"/>

> Liste Exchanges

<img src="Images/Queues.png" alt="Queues" width="500"/>

> Liste Queues

<img src="Images/BindMaster.png" alt="BindMaster" width="350"/>

> Binding Master

<img src="Images/BindSelectionObjet.png" alt="SelectionObjet" width="350"/>

> Binding SelectionObjet

<img src="Images/BindSelectionPiece.png" alt="SelectionPiece" width="350"/>

> Binding SelectionPiece

### Découvrir la réception et l'envoi de messages <a id="RéceptionEnvoiMessages"></a>

#### Test à la main

Essayons de générer un message à partir de l'exchange _master_ ayant une _routing_key_ = Salle de Bain.ampoule_salleDeBain.
Si notre architecture fonctionne, il devrait aller dans les queues _ampoule_salleDeBain_, _Salle de Bain_ et _Maison_.

Bingo !

<img src="Images/Test.png" alt="Test" width="500"/>

#### Script d'envoi

```python
#!/usr/bin/env python
import pika

credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
exchange='Master'
routing_key='Salle de Bain.ampoule_salleDeBain'
body="1"

# Connexion | ConnextionParameters(host, port, virtualHost, credentials)
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, 'client2', credentials))
channel = connection.channel()

# Envoi
channel.basic_publish(exchange, routing_key, body)

print(" [x] Sent '" + body + "' !")

connection.close()
```

#### Script de réception

```python
#!/usr/bin/env python
import pika

credentials = credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')

def callback(ch, method, properties, body):
    print(" [x] Received %s" % body)

# Connexion | ConnextionParameters(host, port, virtualHost, credentials)
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, 'client2', credentials))
channel = connection.channel()

# Réception
channel.basic_consume(queue = 'ampoule_salleDeBain',
                      auto_ack = True,
                      on_message_callback = callback)

print(' [*] Waiting for messages. To exit press CTRL+C')

# Écoute
channel.start_consuming()
```

### Automatisation du déploiement <a id="AutomatisationDéploiement"></a>

Le script suivant nous permet de créer une architecture fonctionnelle pour l'ajout de nouveaux clients. Pas de panique, si le monde s'écroule, ce script se suffit à lui-même, aucune configuration préalable n'est nécessaire :).

```python
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

	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, nomClient, credentials))
	channel = connection.channel()

	# Creation des 3 exchanges
	channel.exchange_declare(exchange = "Master", exchange_type="fanout")
	channel.exchange_declare(exchange = "Selection Piece", exchange_type="topic")
	channel.exchange_declare(exchange = "Selection Objet", exchange_type="topic")

	# Creation de la queue "Maison"
	channel.queue_declare(queue = "Maison")

	# Binding des 3 exchanges et de la queue "Maison"
	channel.exchange_bind(destination = "Selection Piece", source = "Master")
	channel.exchange_bind(destination = "Selection Objet", source = "Master")
	channel.queue_bind(exchange = "Master", queue = "Maison")

	# Creation et Binding des queues pour chaque piece
	for piece in listePieces:
		channel.queue_declare(queue = piece)
		channel.queue_bind(exchange = "Selection Piece", queue = piece, routing_key = piece+".*")

	# Creation et Binding des queues pour chaque objet
	for objet in listeObjets:
		channel.queue_declare(queue = objet)
		channel.queue_bind(exchange = "Selection Objet", queue = objet, routing_key = "*."+objet)

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
```

### Génération automatique de messages <a id="GénérationAutomatique"></a>

Nous allons automatiser la génération automatiques de données de 3 capteurs à l'aide de 3 _docker-compose.yml_ :

#### capteurTemperature :

```yml
version: '3.7'
services:
    moke1:
        image: "pcourbin/mock-data-generator:latest"
        hostname: "moke1"
        environment:
            SENZING_SUBCOMMAND: random-to-rabbitmq
            SENZING_RANDOM_SEED: 0
            SENZING_RECORD_MIN: 1
            SENZING_RECORD_MAX: 100
            SENZING_RECORDS_PER_SECOND: 1
            SENZING_RABBITMQ_HOST: rabbitmq
            SENZING_RABBITMQ_PASSWORD: rabbitmq
            SENZING_RABBITMQ_USERNAME: rabbitmq
            SENZING_RABBITMQ_QUEUE: capteurTemperature
            MIN_VALUE: 15
            MAX_VALUE: 28
            SENZING_DATA_TEMPLATE: '{"nom":"capteurTemperature","date":"date_now", "value":"float"}'
        tty: true
        labels:
            NAME: "moke1"
        networks:
            - iot-labs
networks:
    iot-labs:
        external: true
```

## Stockage des données <a id="Stockage"></a>

Technologie utilisé : __MongoDB__

1. [Définition de l'architecture](#DéfinitionArchitecture)
2. [Déploiement de l'architecture](#DéploiementArchitecture)
3. [Découvrir l'envoi et la réception de messages](#RéceptionEnvoiMessages)
4. [Automatisation du déploiement](#AutomatisationDéploiement)
5. [Génération automatique de messages](#GénérationAutomatique)
6. [Trouver la bonne clé de sharding](#cléSharding)

VH aussi dans mongoDB ?

### Définition de l'architecture <a id="DéfinitionArchitecture"></a>

Chaque client dispose de sa propre base de données. Afin d'offrir un traitement efficace, nous stockons et organisons les données par maison, pièce et objet dans des collections. Les données étant d’ores et déjà organisé de cette manière sur nos serveurs RabbitMQ, il suffit de créer une collection *MongoDB* par queue *RabbitMQ*.

En résumé
* 1 database par client
* 1 collection par queue _RabbitMQ_
* Les données envoyées dans la collection auront le template prédéfini dans l'[Annexe B](#AnnexeB)

### Déploiement de l'architecture <a id="DéploiementArchitecture"></a>

_docker-compose.yml_ permettant de déployer un serveur MongoDB :

```yml
version: '3.1'
services:
    mongo:
        image: mongo:4.2.0-bionic
        hostname: "mongo"
        restart: always
        labels:
            NAME: "mongo"
        networks:
            - iot-labs
        ports:
            - 27017:27017

    mongo-express:
        image: mongo-express:0.49.0
        hostname: "mongo_express"
        restart: always
        ports:
            - 8081:8081
        environment:
             ME_CONFIG_MONGODB_SERVER: mongo
        labels:
            NAME: "mongo_express"
        networks:
            - iot-labs

networks:
    iot-labs:
        external: true
```
Implémentation de l'architecture de Client 2 :

<img src="Images/Database.png" alt="Database" width="400"/>
<img src="Images/Collection.png" alt="Collection" width="400"/>

### Découvrir l'envoi et la réception de messages <a id="RéceptionEnvoiMessages"></a>

#### Script d'envoi

```python
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
```

#### Script de lecture de données

```python
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

# Affichage de la requete
pprint.pprint(collection.find_one())
```
#### Scripts avancés

##### Récupérer la dernière valeur connu d'un capteur

```python
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
```

##### Calculer la moyenne des valeurs d'un capteur entre deux dates fixées

```python
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
results = collection.aggregate(
                            [
                            {"$match": {"nom": sensor_name}},
                            {"$match": {"date": {"$gte": start_date}}},
                            {"$match": {"date": {"$lte": end_date}}},
                            {"$group": {"_id": "$nom", "moyenne": {"$avg": "$temperature"}}}
                           ])

# Affichage de la requete
for result in results:
    print(result)
```

##### Récupérer la valeur minimale d'un capteur entre deux dates fixées

```python
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
```

### Automatisation du déploiement <a id="AutomatisationDéploiement"></a>

Le script suivant nous permet de créer une architecture fonctionnelle pour l'ajout de nouveaux clients. Pas de panique, si le monde s'écroule, ce script se suffit à lui-même, aucune configuration préalable n'est nécessaire (une fois de plus) :).


### Génération automatique de messages <a id="GénérationAutomatique"></a>

Nous allons utiliser une image docker pour connecter une _queue_ de messages à une _collection_ :

Attention à la propriété __AMQPHOST__, il faut préciser l'utilisateur utilisé dans RabbitMQ.

```yml
#https://github.com/marcelmaatkamp/docker-rabbitmq-mongodb
version: '3.7'
services:
    amqp2mongo1:
        image: "marcelmaatkamp/rabbitmq-mongodb"
        hostname: "amqp2mongo1"
        environment:
            AMQPHOST: 'amqp://guest:guest@rabbitmq'
            MONGODB: 'mongodb://mongo/client2'
            MONGOCOLLECTION: 'Maison'
            TRANSLATECONTENT: 'true'
        command: 'Maison'
        tty: true
        labels:
            NAME: "amqp2mongo1"
        networks:
            - iot-labs
        restart: always
networks:
    iot-labs:
        external: true

```

### Trouver la bonne clé de sharding <a id="cléSharding"></a>

## Data Routing <a id="DataRouting"></a>

1. [Déploiement Nifi](#DéploiementNifi)
2. [Récupération des données d'une API](#RécupérationDonnéesAPI)
3. [Récupération données CSV sur serveur FTP](#RécupérationDonnéesCSV)

### Déploiement Nifi <a id="DéploiementNifi"></a>

```yml
version: '3.7'
services:
    nifi:
        image: "apache/nifi:latest"
        hostname: "nifi"
        ports:
            - "8083:8080"
        networks:
            - iot-labs
        labels:
            NAME: "nifi"
networks:
    iot-labs:
        external: true
```



### Récupération des données d'une API <a id="RécupérationDonnéesAPI"></a>
### Récupération données CSV sur serveur FTP <a id="RécupérationDonnéesCSV"></a>



## Annexe

### Annexe A : Descriptif client

Lorsqu'un objet du même type est présent dans différentes pièces, nous ajoutons le nom de la pièce en suffixe au nom de l'objet pour mieux les distinguer.

#### A.1 : Client 1
<a id="AnnexeA1"></a>

| Type                                       | Nom Objet                                                            | Pièce         |
|--------------------------------------------|----------------------------------------------------------------------|---------------|
| 1 détecteur d'ouverture de porte           | detecteurPorte_entree                                                | Entrée        |
| 1 capteur d'activation de lumière          | ampoule_entree                                                       | Entrée        |
| 2 détecteurs d'ouverture de porte          | detecteurPorte1_salon<br>detecteurPorte2_salon                       | Salon         |
| 2 capteurs d'activation de lumière         | ampoule1_salon<br>ampoule2_salon                                     | Salon         |
| 1 détecteur de présence                    | detecteurPresence_salon                                              | Salon         |
| 1 capteur de température                   | capteurTemperature_salon                                             | Salon         |
| 2 capteurs d'activation de chauffage       | radiateur1_salon<br>radiateur2_salon                                 | Salon         |
| 2 capteurs de puissance énergétique        | capteurPuissanceRadiateur1_salon<br>capteurPuissanceRadiateur2_salon | Salon         |
| 2 détecteurs d'ouverture de porte          | detecteurPorte1_chambre<br>detecteurPorte2_chambre                   | Chambre       |
| 1 capteur d'activation de lumière          | ampoule_chambre                                                      | Chambre       |
| 1 détecteur de présence                    | detecteurPresence_chambre                                            | Chambre       |
| 1 capteur de température                   | capteurTemperature_chambre                                           | Chambre       |
| 1 capteur d'activation de chauffage        | radiateur_chambre                                                    | Chambre       |
| 1 détecteur de présence                    | detecteurPresence_cuisine                                            | Cuisine       |
| 1 capteur de température                   | capteurTemperature_cuisine                                           | Cuisine       |
| 1 capteur d'activation de chauffage        | radiateur_cuisine                                                    | Cuisine       |
| 1 capteur d'activation de prise électrique | grillePain                                                           | Cuisine       |
| 1 capteur de consommation énergétique      | capteurConsommationGrillePain                                        | Cuisine       |
| 2 capteurs de puissance énergétique        | capteurPuissanceFour<br>capteurPuissanceMachineLaver                 | Cuisine       |
| 1 capteur de puissance énergétique         | capteurPuissanceBallonEau                                            | Salle de Bain |
| 1 capteur d'activation de chauffage        | radiateur_salleDeBain                                                | Salle de Bain |
| 1 capteur d'activation de lumière          | ampoule_salleDeBain                                                  | Salle de Bain |

#### A.2 : Client 2
<a id="AnnexeA2"></a>

| Type                                |                           | Pièce         |
|-------------------------------------|---------------------------|---------------|
| 1 détecteur de présence             | detecteurPresence         | Principale    |
| 1 capteur d'activation de lumière   | ampoule_principale        | Principale    |
| 1 capteur de température            | capteurTemperature        | Principale    |
| 1 capteur d'activation de chauffage | radiateur_principale      | Principale    |
| 1 capteur d'activation de lumière   | ampoule_salleDeBain       | Salle de Bain |
| 1 capteur de puissance énergétique  | capteurPuissanceBallonEau | Salle de Bain |
| 1 capteur d'activation de chauffage | radiateur_salleDeBain     | Salle de Bain |

### Annexe B : Définition des données <a id="AnnexeB"></a>

1. Détecteur d'ouverture de porte
	* nom : _string_
	* date : _string_
	* valeur : _integer (0 : fermé, 1 : ouvert)_

2. Détecteur de présence
	* nom : _string_
	* date : _string_
	* valeur : _integer (0 : présence non détectée, 1 : présence détectée)_

3. Capteur d'activation de lumière
	* nom : _string_
	* date : _string_
	* valeur : _integer (0 : fermé, 1 : ouvert)_

4. Capteur de luminosité
	* nom : _string_
	* date : _string_
	* luminosite : _double (Lux)_

5. Capteur d'activation de chauffage
	* nom : _string_
	* date : _string_
	* valeur :
		* _0 : Arrêt_
		* _1 : Confort_
		* _2 : Confort -1°C_
		* _3 : Confort -2°C_
		* _4 : Eco_
		* _5 : Hors gel_

6. Capteur d'activation de climatisation
	* nom : _string_
	* date : _string_
	* temperatureCible : _double (°C)_

7. Capteur de température
	* nom : _string_
	* date : _string_
	* temperature : _double (°C)_

8. Capteur d'activation de prise électrique
	* nom :_string_
	* date : _string_
	* valeur : _integer (0 : fermé, 1 : ouvert)_

9. Capteur de consommation énergétique
	* nom : _string_
	* date : _string_
	* consommation : _double (kWh)_

10. Capteur de puissance énergétique
	* nom : _string_
	* date : _string_
	* puissance : _integer (kWh)_

11. Capteur de position
	* nom : _string_
	* date : _string_
	* longitude : _string_
	* latitude : _string_

12. Capteur position volet butée
	* nom : _string_
	* date : _string_
	* valeur : _integer (0 : fermé, 1 : ouvert)_

13. Capteur ordre ouverture volet
	* nom : _string_
	* date : _string_
	* ouverture : _integer (0% : fermé, 100% : ouvert)_
