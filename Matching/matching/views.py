from decouple import config
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from matching.tasks import *
from utils.internal_permission import IsInternalService
from utils.messages import result_message

from .models import JobMatch
from .serializers import InternalMatchingListSerializer


class InternalMatchNewJobToAllCvsTrigger(APIView):
    def post(self, request):
        token = request.headers.get("X-Service-Token")
        if token != config("INTERNAL_SERVICE_TOKEN"):
            return Response({"detail": "Unauthorized"}, status=401)

        job_id = request.data.get("job_id")
        job_description = request.data.get("job_description")

        if not job_id or not job_description:
            result = result_message(
                "ERROR", status.HTTP_400_BAD_REQUEST, {"detail": "Missing fields"}
            )
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        try:
            match_all_cvs_to_new_job.delay(job_id, job_description)
            result = result_message(
                "OK", status.HTTP_200_OK, {"message": "Matching task started"}
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            result = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class InternalMatchNewCvToAllJobsTrigger(APIView):
    def post(self, request):
        token = request.headers.get("X-Service-Token")
        if token != config("INTERNAL_SERVICE_TOKEN"):
            return Response({"detail": "Unauthorized"}, status=401)

        user_id = request.data.get("user_id")
        cv_text = request.data.get("cv_text")

        if not user_id or not cv_text:
            result = result_message(
                "ERROR", status.HTTP_400_BAD_REQUEST, {"detail": "Missing fields"}
            )
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        try:
            match_new_cv_to_all_jobs.delay(user_id, cv_text)
            result = result_message(
                "OK", status.HTTP_200_OK, {"message": "Matching task started"}
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            result = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class InternalMatchList(APIView):
    permission_classes = [IsInternalService]

    def get(self, request):

        try:
            matches = JobMatch.objects.all()
            serializer = InternalMatchingListSerializer(matches, many=True)
            result = result_message("OK", status.HTTP_200_OK, serializer.data)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            resul = result_message("ERROR", status.HTTP_400_BAD_REQUEST, str(e))
            return Response(resul, status=status.HTTP_400_BAD_REQUEST)
