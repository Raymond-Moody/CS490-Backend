from django.shortcuts import render

from rest_framework import viewsets
from .models import Film
from .serializers import FilmSerializer

# Create your views here.
class FilmViewSet(viewsets.ModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer 
