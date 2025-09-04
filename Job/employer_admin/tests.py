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


class JobDetailViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.location = Location.objects.create(title="London")
        self.category = Category.objects.create(title="Engineering")

        # Employer (authorized)
        self.user_id = uuid.uuid4()
        self.token = generate_test_jwt(user_id=self.user_id, role="Employer")
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        # Another employer (unauthorized)
        self.other_id = uuid.uuid4()
        self.other_token = generate_test_jwt(user_id=self.other_id, role="Employer")
        self.other_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.other_token}"}

        # Create a job for main employer
        self.job = Job.objects.create(
            employer_id=self.user_id,
            title="DevOps Engineer",
            location_id=self.location,
            category_id=self.category,
            salary="£60k",
            job_type="Full_time",
            description="Manage cloud infra",
        )

        self.url = reverse(
            "employer_admin:employer_admin_detail", kwargs={"job_id": str(self.job.id)}
        )

    def test_get_job_success(self):
        response = self.client.get(self.url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Result"]["title"], "DevOps Engineer")

    def test_get_job_not_owned(self):
        response = self.client.get(self.url, **self.other_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["Result"], "No Job matches the given query.")

    def test_put_update_job_success(self):
        payload = {
            "title": "Senior DevOps Engineer",
            "salary": "£70k",
            "job_type": "Full_time",
            "description": "Updated role",
            "location_id": self.location.id,
            "category_id": self.category.id,
        }
        response = self.client.put(
            self.url, payload, format="json", **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Result"]["title"], "Senior DevOps Engineer")

    def test_put_invalid_update(self):
        payload = {
            "title": "",  # invalid
            "salary": "£70k",
            "job_type": "InvalidChoice",
            "description": "Bad update",
            "location_id": self.location.id,
            "category_id": self.category.id,
        }
        response = self.client.put(
            self.url, payload, format="json", **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_job_success(self):
        response = self.client.delete(self.url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Message"], "DELETED")
        self.assertFalse(Job.objects.filter(id=self.job.id).exists())

    def test_delete_job_not_owned(self):
        response = self.client.delete(self.url, **self.other_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["Result"], "No Job matches the given query.")

    def test_unauthenticated_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
