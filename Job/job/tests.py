# import uuid

# from django.contrib.auth import get_user_model
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient, APITestCase

# from .models import Category, Job, Location
# from .serializers import JobSerializer


# class JobAPITestCase(APITestCase):

#     def setUp(self):
#         self.client = APIClient()

#         # Create sample Location and Category
#         self.location = Location.objects.create(title="Manchester")
#         self.category = Category.objects.create(title="Software Development")

#         # Create sample job
#         self.job = Job.objects.create(
#             employer_id=uuid.uuid4(),
#             title="Django Developer",
#             location_id=self.location,
#             category_id=self.category,
#             salary="£40,000",
#             job_type="Full_time",
#             status=True,
#             description="We are hiring Django developers.",
#         )

#         self.list_url = reverse("job:job_list")
#         self.detail_url = reverse("job:job_detail", args=[self.job.id])

#     def test_get_job_list(self):
#         """Test retrieving all jobs"""
#         response = self.client.get(self.list_url)
#         jobs = Job.objects.all()
#         serializer = JobSerializer(jobs, many=True)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["Message"], "OK")
#         self.assertEqual(response.data["Result"], serializer.data)

#     def test_get_job_detail(self):
#         """Test retrieving a single job by ID"""
#         response = self.client.get(self.detail_url)
#         job = Job.objects.get(id=self.job.id)
#         serializer = JobSerializer(job)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["Message"], "OK")
#         self.assertEqual(response.data["Result"], serializer.data)

#     def test_get_job_detail_not_found(self):
#         """Test retrieving a non-existing job"""
#         invalid_url = reverse("job:job_detail", args=[uuid.uuid4()])
#         response = self.client.get(invalid_url)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["Message"], "ERROR")
