import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.messages import result_message

from .models import *
from .serializers import *


class ApplicationList(APIView):

    def get(self, request):
        user_id = request.user.id

        try:
            applicatios = Application.objects.filter(user_id=user_id)
            serializer = ApplicationSerializer(applicatios, many=True)
            resul = result_message("OK", status.HTTP_200_OK, serializer.data)
            return Response(resul, status=status.HTTP_200_OK)
        except Exception as e:
            resul = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(resul, status=status.HTTP_400_BAD_REQUEST)

    def post(sell, request):
        user_id = request.user.id
        job_id = request.data.get("job_id")

        try:
            job_data = request.data.copy()
            job_data["user_id"] = user_id

            job_check = requests.get(f"http://localhost:8000/api/job/{job_id}/")
            if job_check.status_code != 200:
                resul = result_message(
                    "ERROR",
                    status.HTTP_400_BAD_REQUEST,
                    {"error": "Invalid or non-existent job"},
                )
                return Response(resul, status=status.HTTP_400_BAD_REQUEST)

            serializer = ApplicationSerializer(data=job_data)
            if serializer.is_valid():
                serializer.save()
                resul = result_message(
                    "CREATED", status.HTTP_201_CREATED, serializer.data
                )
                return Response(resul, status=status.HTTP_201_CREATED)
            else:
                resul = result_message(
                    "ERROR", status.HTTP_400_BAD_REQUEST, serializer.errors
                )
                return Response(resul, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            resul = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(resul, status=status.HTTP_400_BAD_REQUEST)
