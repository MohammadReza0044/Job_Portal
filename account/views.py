from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import InputRegisterSerializer, OutPutRegisterSerializer


class Register(APIView):
    def post(self, request):
        serializer = InputRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.create(
                email=serializer.validated_data.get("email"),
                password=make_password(serializer.validated_data["password"]),
                first_name=serializer.validated_data.get("first_name"),
                last_name=serializer.validated_data.get("last_name"),
                role=serializer.validated_data.get("role"),
            )

        except Exception as ex:
            return Response(f"Database Error {ex}", status=status.HTTP_400_BAD_REQUEST)
        return Response(
            OutPutRegisterSerializer(user, context={"request": request}).data
        )
