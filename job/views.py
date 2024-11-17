from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from messages import result_message

from .models import Job
from .serializers import *


class JobList(APIView):
    def get(self, request):
        user_id = request.user.id

        try:
            jobs = Job.objects.filter(employer_id=user_id)
            serializer = JobSerializer(jobs, many=True)
            resul = result_message("OK", status.HTTP_200_OK, serializer.data)
            return Response(resul, status=status.HTTP_200_OK)
        except Exception as e:
            resul = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(resul, status=status.HTTP_400_BAD_REQUEST)

    def post(sell, request):
        user_id = request.user.id

        try:
            job_data = request.data.copy()
            job_data["employer"] = user_id

            serializer = JobSerializer(data=job_data)
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


class JobDetail(APIView):
    def get(self, request, job_id):
        pass

    def put(self, request, job_id):
        pass

    def delete(self, request, job_id):
        pass
