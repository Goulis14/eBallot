# voting/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings


class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=[('Admin', 'Admin'), ('Voter', 'Voter')],
        default='Voter'
    )

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Προσαρμοσμένο related_name για αποφυγή σύγκρουσης
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Προσαρμοσμένο related_name για αποφυγή σύγκρουσης
        blank=True
    )


class Election(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    active_from = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Candidate(models.Model):
    name = models.CharField(max_length=255)
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='candidates'
    )


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
