#!/usr/bin/env python
import pika

credentials = credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')

def callback(ch, method, properties, body):
    print(" [x] Received %s" % body)

# Connexion
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, 'client2', credentials))
channel = connection.channel()

# Réception
channel.basic_consume(queue = 'ampoule_salleDeBain',
                      auto_ack = True,
                      on_message_callback = callback)

print(' [*] Waiting for messages. To exit press CTRL+C')

# Écoute
channel.start_consuming()
