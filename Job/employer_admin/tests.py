import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from job.models import Category, Job, Location
from utils.generate_jwt import generate_test_jwt


class JobListViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("employer_admin:admin_job_list")
        # create supporting objects
        self.location = Location.objects.create(title="Manchester")
        self.category = Category.objects.create(title="IT")

        # employer id from token must match Job.employer_id
        self.user_id = uuid.uuid4()
        self.token = generate_test_jwt(user_id=self.user_id, role="Employer")
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

    def test_get_jobs_empty(self):
        """Employer with no jobs should get empty list"""
        response = self.client.get(self.url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Result"], [])

    def test_get_jobs_with_results(self):
        """Employer should see only their jobs"""
        Job.objects.create(
            employer_id=str(self.user_id),
            title="Backend Developer",
            location_id=self.location,
            category_id=self.category,
            salary="£40k",
            job_type="Full_time",
            description="Django backend dev role",
        )
        response = self.client.get(self.url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["Result"]), 1)
        self.assertEqual(response.data["Result"][0]["title"], "Backend Developer")

    def test_post_create_job_success(self):
        """Employer can create a job successfully"""
        payload = {
            "title": "Python Developer",
            "location_id": self.location.id,
            "category_id": self.category.id,
            "salary": "£50k",
            "job_type": "Full_time",
            "description": "Exciting role with Django",
        }
        response = self.client.post(
            self.url, payload, format="json", **self.auth_headers
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["Result"]["title"], "Python Developer")

    def test_post_create_job_invalid(self):
        """Invalid job data should return 400"""
        payload = {
            "title": "",  # missing title
            "location_id": self.location.id,
            "category_id": self.category.id,
            "salary": "£30k",
            "job_type": "InvalidType",  # wrong choice
            "description": "test",
        }
        response = self.client.post(
            self.url, payload, format="json", **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_request(self):
        """Missing token should be rejected"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
