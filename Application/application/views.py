import requests
from decouple import config
from pdfminer.high_level import extract_text
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView

from utils.internal_permission import IsInternalService
from utils.messages import result_message

from .models import *
from .serializers import *


class ApplicationList(ListCreateAPIView):
    serializer_class = ApplicationSerializer
    filterset_fields = ["status"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Application.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        job_id = request.data.get("job_id")

        try:
            if Application.objects.filter(user_id=user_id, job_id=job_id).exists():
                result = result_message(
                    "ERROR",
                    status.HTTP_400_BAD_REQUEST,
                    {"error": "You have already applied for this job"},
                )
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            url = config("JOB_SERVICE_URL") + f"/api/v1/internal/jobs/{job_id}/"
            headers = {"X-Service-Token": config("INTERNAL_SERVICE_TOKEN")}
            job_check = requests.get(url, headers=headers, timeout=5)
            if job_check.status_code != 200:
                result = result_message(
                    "ERROR",
                    status.HTTP_400_BAD_REQUEST,
                    {"error": "Invalid or non-existent job"},
                )
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            data = request.data.copy()
            data["user_id"] = user_id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                result = result_message(
                    "CREATED", status.HTTP_201_CREATED, serializer.data
                )
                return Response(result, status=status.HTTP_201_CREATED)

            result = result_message(
                "ERROR", status.HTTP_400_BAD_REQUEST, serializer.errors
            )
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            result = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class CvList(APIView):

    def get(self, request):
        user_id = request.user.id

        try:
            cv = UserCV.objects.get(user_id=user_id)

            serializer = UserCVSerializer(cv)

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

    def post(self, request):
        user_id = request.user.id

        if UserCV.objects.filter(user_id=user_id).exists():
            result = result_message(
                "ERROR",
                status.HTTP_400_BAD_REQUEST,
                {"error": "A CV already exists."},
            )

            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer = UserCVSerializer(data=request.data)

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

            instance = serializer.save(
                user_id=user_id,
                full_name=(
                    f"{request.user.first_name} " f"{request.user.last_name}"
                ).strip(),
            )

            # Extract text from the saved CV
            try:
                if instance.cv_file:
                    file_path = instance.cv_file.path

                    text = extract_text(file_path)

                    instance.extracted_text = text.strip()

                    instance.save(update_fields=["extracted_text"])

            except Exception as e:
                print(f"Error extracting text from CV: {e}")

                instance.extracted_text = ""

                instance.save(update_fields=["extracted_text"])

            # Trigger Matching Service
            try:
                headers = {"X-Service-Token": config("INTERNAL_SERVICE_TOKEN")}

                payload = {
                    "user_id": str(user_id),
                    "cv_text": instance.extracted_text,
                }

                matching_url = (
                    config("MATCHING_SERVICE_URL")
                    + "/api/v1/internal/"
                    + "trigger-matching-new-cv-to-jobs/"
                )

                response = requests.post(
                    matching_url,
                    headers=headers,
                    json=payload,
                    timeout=5,
                )

                response.raise_for_status()

                print("CV indexing and matching tasks " "triggered successfully")

            except Exception as e:
                print(f"Failed to notify matching service: {e}")

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

    def delete(self, request):
        user_id = request.user.id

        try:
            cv = UserCV.objects.get(user_id=user_id)

            cv.delete()

            try:
                headers = {"X-Service-Token": config("INTERNAL_SERVICE_TOKEN")}

                payload = {
                    "user_id": str(user_id),
                }

                MATCHING_URL = (
                    config("MATCHING_SERVICE_URL")
                    + "/api/v1/internal/trigger-delete-cv/"
                )

                response = requests.post(
                    MATCHING_URL,
                    headers=headers,
                    json=payload,
                    timeout=5,
                )

                response.raise_for_status()

            except Exception as e:
                print(f"Failed to notify matching service about CV deletion: {e}")

            return Response(status=status.HTTP_204_NO_CONTENT)

        except UserCV.DoesNotExist:
            result = result_message(
                "ERROR",
                status.HTTP_404_NOT_FOUND,
                {"error": "CV not found."},
            )

            return Response(
                result,
                status=status.HTTP_404_NOT_FOUND,
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


class InternalCVList(APIView):
    permission_classes = [IsInternalService]

    def get(self, request):

        try:
            cvs = UserCV.objects.all()
            serializer = InternalCVListSerializer(cvs, many=True)
            return Response(serializer.data)
        except Exception as e:
            resul = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(resul, status=status.HTTP_400_BAD_REQUEST)
