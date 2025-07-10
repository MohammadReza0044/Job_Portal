import uuid

from django.db import models


class Location(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "Location"


class Category(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "Category"


class Job(models.Model):
    JOB_TYPE = (
        ("Full_time", "Full_time"),
        ("Part_time", "Part_time"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employer_id = models.UUIDField()
    title = models.CharField(max_length=255)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    salary = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "Job"
