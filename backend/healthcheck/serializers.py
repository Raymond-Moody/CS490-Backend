from rest_framework import serializers

class HealthCheck:
    def __init__(self):
        self.message = "Hello, World!"

class HealthCheckSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=256)

