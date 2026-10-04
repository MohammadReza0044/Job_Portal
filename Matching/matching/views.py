from decouple import config
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from matching.tasks import *
from utils.internal_permission import IsInternalService
from utils.messages import result_message

from .models import JobMatch
from .serializers import InternalMatchingListSerializer
from matching.services.mongodb_vector_store import update_job_status


class InternalMatchNewJobToAllCvsTrigger(APIView):
    def post(self, request):
        token = request.headers.get("X-Service-Token")

        if token != config("INTERNAL_SERVICE_TOKEN"):
            return Response(
                {"detail": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        job_id = request.data.get("job_id")
        job_description = request.data.get("job_description")

        if not job_id or not job_description:
            result = result_message(
                "ERROR",
                status.HTTP_400_BAD_REQUEST,
                {"detail": "Missing fields"},
            )
            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            match_new_job_to_all_cvs.delay(
                job_id,
                job_description,
            )

            result = result_message(
                "OK",
                status.HTTP_200_OK,
                {"message": "Matching task started"},
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


class InternalDeleteCvTrigger(APIView):
    def post(self, request):
        token = request.headers.get("X-Service-Token")

        if token != config("INTERNAL_SERVICE_TOKEN"):
            return Response(
                {"detail": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_id = request.data.get("user_id")

        if not user_id:
            result = result_message(
                "ERROR",
                status.HTTP_400_BAD_REQUEST,
                {"detail": "user_id is required"},
            )

            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            remove_cv_vector.delay(user_id)

            result = result_message(
                "OK",
                status.HTTP_200_OK,
                {"message": "CV deletion task started"},
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


class InternalMatchNewCvToAllJobsTrigger(APIView):
    def post(self, request):
        token = request.headers.get("X-Service-Token")

        if token != config("INTERNAL_SERVICE_TOKEN"):
            return Response(
                {"detail": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_id = request.data.get("user_id")
        cv_text = request.data.get("cv_text")

        if not user_id or not cv_text:
            result = result_message(
                "ERROR",
                status.HTTP_400_BAD_REQUEST,
                {"detail": "Missing fields"},
            )

            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 1. Create CV embedding and store it in IndexedCV + FAISS
            index_cv.delay(
                user_id,
                cv_text,
            )

            # 2. Match the new CV against existing active jobs
            match_new_cv_to_all_jobs.delay(
                user_id,
                cv_text,
            )

            result = result_message(
                "OK",
                status.HTTP_200_OK,
                {"message": ("CV indexing and matching tasks " "started successfully")},
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


class JobEventView(APIView):

    def post(self, request):
        service_token = request.headers.get("X-Service-Token")

        if service_token != config("INTERNAL_SERVICE_TOKEN"):
            return Response(
                {"detail": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        event = request.data.get("event")
        job_id = request.data.get("job_id")
        data = request.data.get("data", {})

        if not event or not job_id:
            return Response(
                {"detail": "event and job_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if event in ["job.created", "job.updated"]:

            sync_job_vector.delay(job_id)

        elif event == "job.status_changed":

            new_status = data.get("status")

            print(
                f"STATUS EVENT: "
                f"job_id={job_id}, "
                f"new_status={new_status!r}, "
                f"type={type(new_status)}"
            )

            update_job_status(
                job_id=job_id,
                is_active=new_status,
            )

            if new_status is False:
                deleted_count, _ = JobMatch.objects.filter(job_id=job_id).delete()

                print(
                    f"DEACTIVATED JOB {job_id}: "
                    f"deleted {deleted_count} JobMatch rows"
                )

        elif event == "job.deleted":

            JobMatch.objects.filter(job_id=job_id).delete()

            remove_job_vector.delay(job_id)
        return Response(
            {"status": "processed"},
            status=status.HTTP_200_OK,
        )


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
