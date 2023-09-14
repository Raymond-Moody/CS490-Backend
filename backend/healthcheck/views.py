from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .serializers import HealthCheckSerializer
from .serializers import HealthCheck
from rest_framework.response import Response

class HealthCheckView(viewsets.ViewSet):
    def list(self, request):
        serializer = HealthCheckSerializer(HealthCheck())
        return Response(serializer.data)

