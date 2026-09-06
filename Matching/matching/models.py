import uuid

from django.db import models


class JobMatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    job_id = models.UUIDField()
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "Job Match"


class IndexedJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_id = models.UUIDField(unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    # This is the integer ID used inside FAISS
    faiss_index_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.job_id)

    class Meta:
        db_table = "Indexed Job"
