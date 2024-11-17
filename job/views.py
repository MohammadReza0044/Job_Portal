from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from messages import result_message

from .models import Job
from .permissions import IsEmployer
from .serializers import *


class JobList(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsEmployer()]
        return super().get_permissions()

    def get(self, request):
        user_id = request.user.id

        try:
            if request.user.role == "Employer":
                jobs = Job.objects.filter(employer_id=user_id)
            else:
                jobs = Job.objects.all()

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
    def get_permissions(self):
        if self.request.method in ["PUT", "DELETE"]:
            return [IsEmployer()]
        return super().get_permissions()

    def get(self, request, job_id):
        user_id = request.user.id

        try:
            job = get_object_or_404(Job, employer=user_id, id=job_id)
            serializer = JobSerializer(job)
            result = result_message("OK", status.HTTP_200_OK, serializer.data)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            result = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, job_id):
        user_id = request.user.id

        try:
            job = get_object_or_404(Job, employer=user_id, id=job_id)
            serializer = JobUpdateSerializer(job, data=request.data)
            if serializer.is_valid():
                serializer.save()
                result = result_message("OK", status.HTTP_200_OK, serializer.data)
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = result_message(
                    "ERROR", status.HTTP_400_BAD_REQUEST, serializer.errors
                )
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, job_id):
        user_id = request.user.id

        try:
            get_object_or_404(Job, employer=user_id, id=job_id).delete()
            result = result_message("DELETED", status.HTTP_204_NO_CONTENT, "DELETED")
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            result = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
