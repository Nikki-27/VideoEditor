from django.urls import path
from .views import TaskListCreateView,VideoUploadView


urlpatterns = [
    path('api/tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('api/upload/', VideoUploadView.as_view(), name='video-upload'),
]
