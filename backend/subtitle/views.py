from django.shortcuts import render
from rest_framework import generics
from .models import Task
from .serializers import TaskSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework import status

class VideoUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        file_obj = request.data['video']
        # Do something with the uploaded video file, like saving to disk or database
        return Response(status=status.HTTP_201_CREATED)


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
