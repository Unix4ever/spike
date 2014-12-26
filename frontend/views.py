from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import generics

from frontend import models
from frontend import tasks


class TaskView(generics.RetrieveUpdateDestroyAPIView):
    """
    Tasks related apis
    """
    queryset = models.Task.objects.all()
    serializer_class = models.TaskSerializer

class TaskList(generics.ListCreateAPIView):
    queryset = models.Task.objects.all()
    serializer_class = models.TaskSerializer

    def perform_create(self, serializer):
        task = serializer.save()
        tasks.add_tasks.apply_async((task,))


class ScenarioView(generics.RetrieveUpdateDestroyAPIView):
    """
    Scenarios related apis
    """
    queryset = models.Scenario.objects.all()
    serializer_class = models.ScenarioSerializer

class ScenarioList(generics.ListCreateAPIView):
    queryset = models.Scenario.objects.all()
    serializer_class = models.ScenarioSerializer
