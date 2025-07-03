import uuid

from django.db import models


class Application(models.Model):
    STATUS_CHOICES = (
        ("Applied", "Applied"),
        ("In_Progress", "In Progress"),
        ("Interviewing", "Interviewing"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    job_id = models.UUIDField(db_index=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Applied")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "Application"


class JobSeekerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True, db_index=True)
    full_name = models.CharField(max_length=100)
    cv_file = models.FileField(upload_to="cvs/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = "Job Seeker Profile"
