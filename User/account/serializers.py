from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class InputRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=get_user_model().ROLE_CHOICES)
    password = serializers.CharField(max_length=255)
    confirm_password = serializers.CharField(max_length=255)

    def validate_phone_number(self, email):
        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is exist")
        return email

    def validate(self, data):
        if not data.get("password") or not data.get("confirm_password"):
            raise serializers.ValidationError(
                "Please fill password and confirm password"
            )

        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError(
                "confirm password is not equal to password"
            )
        return data


class OutPutRegisterSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField("get_token")

    class Meta:
        model = get_user_model()
        fields = ("email", "token", "role", "created_at", "updated_at")

    def get_token(self, user):
        data = dict()
        token_class = RefreshToken

        refresh = token_class.for_user(user)

        # Add custom claims to both tokens
        refresh["role"] = user.role
        refresh["email"] = user.email

        # 👇 Access token must have them too
        access = refresh.access_token
        access["role"] = user.role
        access["email"] = user.email

        data["refresh"] = str(refresh)
        data["access"] = str(access)

        print("Generated JWT with claims:", access.payload)  # Debug: Check output

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        print(data)

        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["role"] = user.role
        token["email"] = user.email

        return token


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ("email", "first_name", "last_name", "role")


class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, required=False)
    last_name = serializers.CharField(max_length=255, required=False)
    role = serializers.ChoiceField(
        choices=get_user_model().ROLE_CHOICES, required=False
    )

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "role")
