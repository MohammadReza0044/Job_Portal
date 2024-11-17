from django.contrib.auth import get_user_model
from django.db import models


class Job(models.Model):
    JOB_TYPE = (
        ("Full_time", "Full_time"),
        ("Part_time", "Part_time"),
    )

    employer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    salary = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "Job"
