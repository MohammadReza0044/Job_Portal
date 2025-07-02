import uuid

from django.db import models


class Application(models.Model):
    STATUS_TYPE = (
        ("Applied", "Applied"),
        ("In_Progress", "In_Progress"),
        ("Interviewing", "Interviewing"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    job_id = models.UUIDField()
    status = models.CharField(max_length=50, choices=STATUS_TYPE, default="Applied")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

    class Meta:
        db_table = "Application"
