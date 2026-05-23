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
    filterset_fields = ["status", "job_id"]
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


class ProfileList(APIView):

    def get(self, request):
        user_id = request.user.id

        try:
            profile = JobSeekerProfile.objects.filter(user_id=user_id)
            serializer = JobSeekerProfileSerializer(profile, many=True)
            resul = result_message("OK", status.HTTP_200_OK, serializer.data)
            return Response(resul, status=status.HTTP_200_OK)
        except Exception as e:
            resul = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(resul, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        user_id = request.user.id
        user_name = f"{request.user.first_name} {request.user.last_name}"

        if JobSeekerProfile.objects.filter(user_id=user_id).exists():
            resul = result_message(
                "ERROR",
                status.HTTP_400_BAD_REQUEST,
                {"error": "A profile already exists. Use PUT to update it."},
            )
            return Response(resul, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile_data = request.data.copy()
            profile_data["user_id"] = user_id
            profile_data["full_name"] = user_name

            serializer = JobSeekerProfileSerializer(data=profile_data)
            if serializer.is_valid():
                instance = serializer.save()

                # Extract text from the saved file
                try:
                    if instance.cv_file:
                        file_path = instance.cv_file.path  # full path to file on disk
                        text = extract_text(file_path)
                        instance.extracted_text = text.strip()
                        instance.save(update_fields=["extracted_text"])
                except Exception as e:
                    print(f"Error extracting text from CV: {e}")
                    instance.extracted_text = ""
                    instance.save(update_fields=["extracted_text"])

                # ✅ Trigger matching service here
                try:
                    headers = {"X-Service-Token": config("INTERNAL_SERVICE_TOKEN")}
                    payload = {
                        "user_id": str(user_id),
                        "cv_text": instance.extracted_text,
                    }
                    MATCHING_URL = (
                        config("MATCHING_SERVICE_URL")
                        + "/api/v1/internal/trigger-matching-new-cv-to-jobs/"
                    )
                    requests.post(
                        MATCHING_URL, headers=headers, json=payload, timeout=5
                    )
                    print("message has been sent to matching service")
                except Exception as e:
                    print(f"Failed to notify matching service: {e}")

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


class InternalCVList(APIView):
    permission_classes = [IsInternalService]

    def get(self, request):

        try:
            cvs = JobSeekerProfile.objects.all()
            serializer = InternalCVListSerializer(cvs, many=True)
            return Response(serializer.data)
        except Exception as e:
            resul = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(resul, status=status.HTTP_400_BAD_REQUEST)
