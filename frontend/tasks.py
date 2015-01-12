import pika
import logging
import json

from pika import credentials as pika_credentials

from frontend.celery import app
from django.conf import settings
from rest_framework import serializers

from frontend import models


class QueueTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for task
    """
    id = serializers.CharField(read_only=True)
    end_time = serializers.DateTimeField(read_only=True)
    running = serializers.BooleanField(read_only=True)
    scenario = models.ScenarioSerializer(read_only=True)

    class Meta(object):
        model = models.Task
        fields = ('id', 'scenario')


@app.task(bind=True)
def add_tasks(self, task):
    """
    Add load testing tasks to the queue
    """
    message = QueueTaskSerializer().to_representation(task)
    message["host"] = settings.EXTERNAL_ADDRESS
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=str(settings.AMQP_HOST),
            credentials=pika_credentials.PlainCredentials(settings.AMQP_USER, settings.AMQP_PASS)))
    channel = connection.channel()

    serialized_message = json.dumps(message)

    for _ in xrange(task.run_count):
        channel.basic_publish(exchange='',
                routing_key=settings.AMQP_QUEUE,
                body=serialized_message)

    connection.close()
