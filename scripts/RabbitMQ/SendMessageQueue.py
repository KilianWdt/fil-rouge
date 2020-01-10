#!/usr/bin/env python
import pika

credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
exchange = 'Master'
routing_key = 'Salle de Bain.ampoule_salleDeBain'
body = "1"

# Connexion
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', 5672, 'client2', credentials))
channel = connection.channel()

# Envoi
channel.basic_publish(exchange, routing_key, body)
print(" [x] Sent '" + body + "' !")

# Fermer connexion
connection.close()
