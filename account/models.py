import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager as BUM
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class BaseUserManager(BUM):
    def create_user(
        self,
        email,
        password=None,
        is_active=True,
        is_staff=False,
        is_admin=False,
        is_superuser=False,
        role=None,
        **extra_fields
    ):
        if not email:
            raise ValueError("Users must have a email")

        user = self.model(
            email=self.normalize_email(email),
            is_active=is_active,
            is_staff=is_staff,
            is_admin=is_admin,
            is_superuser=is_superuser,
            role=role,
            **extra_fields,
        )

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "Admin")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("Employer", "Employer"),
        ("Job_Seeker", "Job_Seeker"),
        ("Admin", "Admin"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="Job_Seeker")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BaseUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    class Meta:
        db_table = "User"
