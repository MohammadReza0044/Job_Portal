import requests
from decouple import config
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from django.db import transaction

from .tasks import notify_matching_service


from job.permissions import IsEmployer
from job.serializers import *
from utils.messages import result_message

from .models import *
from job.permissions import *
from job.serializers import *


class JobList(ListCreateAPIView):
    permission_classes = [IsEmployer]
    serializer_class = JobSerializer
    filterset_fields = ["status"]
    ordering_fields = ["category_id__title", "location_id__title", "job_type"]
    ordering = ["salary", "created_at"]

    def get_queryset(self):
        return Job.objects.filter(employer_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        user_id = request.user.id

        try:
            job_data = request.data.copy()
            job_data["employer_id"] = user_id
            job_data["status"] = True

            serializer = JobSerializer(data=job_data)

            if not serializer.is_valid():
                result = result_message(
                    "ERROR",
                    status.HTTP_400_BAD_REQUEST,
                    serializer.errors,
                )
                return Response(
                    result,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                job = serializer.save()

                transaction.on_commit(
                    lambda: notify_matching_service.delay(
                        event="job.created",
                        job_id=str(job.id),
                    )
                )

            result = result_message(
                "CREATED",
                status.HTTP_201_CREATED,
                serializer.data,
            )

            return Response(
                result,
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            result = result_message(
                "ERROR",
                status.HTTP_400_BAD_REQUEST,
                str(e),
            )

            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )


class JobDetail(APIView):
    permission_classes = [IsEmployer]

    def get(self, request, job_id):
        user_id = request.user.id

        try:
            job = get_object_or_404(Job, employer_id=user_id, id=job_id)
            serializer = JobSerializer(job)
            result = result_message("OK", status.HTTP_200_OK, serializer.data)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            result = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, job_id):
        user_id = request.user.id

        try:
            job = get_object_or_404(
                Job,
                employer_id=user_id,
                id=job_id,
            )

            serializer = JobUpdateSerializer(
                job,
                data=request.data,
                partial=True,
            )

            if not serializer.is_valid():
                result = result_message(
                    "ERROR",
                    status.HTTP_400_BAD_REQUEST,
                    serializer.errors,
                )
                return Response(
                    result,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                job = serializer.save()

                transaction.on_commit(
                    lambda: notify_matching_service.delay(
                        event="job.updated",
                        job_id=str(job.id),
                        data={
                            "status": job.status,
                        },
                    )
                )

            result = result_message(
                "OK",
                status.HTTP_200_OK,
                serializer.data,
            )

            return Response(
                result,
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            result = result_message(
                "ERROR",
                status.HTTP_400_BAD_REQUEST,
                str(e),
            )

            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, job_id):
        user_id = request.user.id

        try:
            job = get_object_or_404(
                Job,
                employer_id=user_id,
                id=job_id,
            )

            deleted_job_id = str(job.id)

            with transaction.atomic():
                job.delete()

                transaction.on_commit(
                    lambda: notify_matching_service.delay(
                        event="job.deleted",
                        job_id=deleted_job_id,
                    )
                )

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            result = result_message(
                "ERROR",
                status.HTTP_400_BAD_REQUEST,
                str(e),
            )

            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )


class LocationList(ListCreateAPIView):
    permission_classes = [IsEmployer]
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
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


class CategoryList(ListCreateAPIView):
    permission_classes = [IsEmployer]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
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
