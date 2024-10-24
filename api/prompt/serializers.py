from rest_framework import serializers

from .models import Prompt, Role


class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = "__all__"


class CreatePromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ["text_data", "name"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class CreateRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["description", "name", "tone_of_voice"]
