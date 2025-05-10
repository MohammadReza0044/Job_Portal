from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.messages import result_message

from .serializers import *


class Register(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InputRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = get_user_model().objects.create(
                email=serializer.validated_data.get("email"),
                password=make_password(serializer.validated_data["password"]),
                first_name=serializer.validated_data.get("first_name"),
                last_name=serializer.validated_data.get("last_name"),
                role=serializer.validated_data.get("role"),
            )

        except Exception as e:
            return Response(f"Database Error {e}", status=status.HTTP_400_BAD_REQUEST)
        return Response(
            OutPutRegisterSerializer(user, context={"request": request}).data
        )


class Profile(APIView):
    def get(self, request):
        user_id = request.user.id
        user = get_object_or_404(get_user_model(), id=user_id)
        serializer = ProfileSerializer(user)

        try:
            result = result_message("OK", status.HTTP_200_OK, serializer.data)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            result = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user_id = request.user.id
        user = get_object_or_404(get_user_model(), id=user_id)
        serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)

        try:
            if serializer.is_valid():
                serializer.save()
                result = result_message("UPDATED", status.HTTP_200_OK, serializer.data)
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = result_message(
                    "ERROR", status.HTTP_400_BAD_REQUEST, serializer.errors
                )
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
