import os

from django.utils.encoding import smart_unicode

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import generics
from rest_framework import renderers

from frontend import models
from frontend import tasks
from frontend import settings


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        print data
        return data.encode(self.charset)


@api_view(['GET'])
@renderer_classes((renderers.JSONRenderer, PlainTextRenderer))
def get_file(request, pk, format=None):
    """
    Get script file
    """
    try:
        scenario = models.Scenario.objects.get(id=pk)
    except models.Scenario.DoesNotExist:
        return Response({"error": "No such scenario"}, status=404)

    return Response(scenario.scenario_file.read())


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
