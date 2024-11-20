# serializers.py
from rest_framework import serializers
from .models import DataEntry  # Adjust the import according to your model

class CombinedDataEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DataEntry  # Use your actual model here
        fields = '__all__'  # Specify fields if needed