import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from job.models import Category, Job, Location
from utils.generate_jwt import generate_test_jwt


class AuthenticatedJobViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Supporting objects
        self.location = Location.objects.create(title="London")
        self.category = Category.objects.create(title="Engineering")

        # Authorized user
        self.user_id = uuid.uuid4()
        self.token = generate_test_jwt(user_id=self.user_id, role="Employer")
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        # Jobs
        self.job1 = Job.objects.create(
            employer_id=uuid.uuid4(),
            title="Backend Developer",
            location_id=self.location,
            category_id=self.category,
            salary="£40k",
            job_type="Full_time",
            description="Backend dev role",
        )
        self.job2 = Job.objects.create(
            employer_id=uuid.uuid4(),
            title="Frontend Developer",
            location_id=self.location,
            category_id=self.category,
            salary="£35k",
            job_type="Part_time",
            description="Frontend dev role",
        )

    def test_get_all_jobs(self):
        url = reverse("job:job_list")
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["Result"]), 2)

    def test_get_single_job(self):
        url = reverse("job:job_detail", kwargs={"job_id": str(self.job1.id)})
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Result"]["title"], "Backend Developer")

    def test_get_jobs_unauthenticated(self):
        url = reverse("job:job_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_single_job_unauthenticated(self):
        url = reverse("job:job_detail", kwargs={"job_id": str(self.job1.id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
