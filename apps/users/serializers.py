from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User

# User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["name", "email", "password"]

    def create(self, validated_data):

        full_name = validated_data.pop("name")

        first_name = ""
        last_name = ""

        if full_name:
            parts = full_name.split(" ")
            first_name = parts[0]
            last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=first_name,
            last_name=last_name
        )

        return user