import uuid

from django.db import models

from rest_framework import serializers


class Scenario(models.Model):
    """
    Load test scenario
    """
    SCENARIO_TYPES = (
        ("python", "Python"),
    )
    # id of scenario
    id = models.CharField(max_length=256, primary_key=True, default=lambda: uuid.uuid4().hex)
    # scenario type
    type = models.CharField(max_length=32, choices=SCENARIO_TYPES)
    # scenario file link
    scenario_file = models.FileField(upload_to="scenarios/files/")


class Task(models.Model):
    """
    Load testing task
    """
    # id of the task
    id = models.CharField(max_length=32, default=lambda: uuid.uuid4().hex, primary_key=True)
    # scenario id to launch
    scenario = models.ForeignKey(Scenario)
    # is running
    running = models.BooleanField(default=False)
    # run count
    run_count = models.IntegerField()
    # load test start time
    start_time = models.DateTimeField(auto_now_add=True)
    # load test end time
    end_time = models.DateTimeField(auto_now_add=True)
   

class ScenarioSerializer(serializers.ModelSerializer):
    """
    Serializer for scenario
    """
    id = serializers.CharField(read_only=True)

    class Meta(object):
        model = Scenario
        fields = ('id', 'type', 'scenario_file')

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for task
    """
    id = serializers.CharField(read_only=True)
    end_time = serializers.DateTimeField(read_only=True)
    running = serializers.BooleanField(read_only=True)
    scenario = ScenarioSerializer

    class Meta(object):
        model = Task
        fields = ('id', 'scenario', 'running', 'start_time', 'end_time', 'run_count')
    
