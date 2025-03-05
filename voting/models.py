# voting/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings


class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Prefer not to say', 'Prefer not to say')
    ]

    AGE_GROUPS = [
        ('18-25', '18-25'),
        ('26-35', '26-35'),
        ('36-45', '36-45'),
        ('46-60', '46-60'),
        ('60+', '60+'),
    ]

    role = models.CharField(
        max_length=20,
        choices=[('Admin', 'Admin'), ('Voter', 'Voter')],
        default='Voter'
    )

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default='Prefer not to say'
    )

    age_group = models.CharField(
        max_length=10,choices=AGE_GROUPS, null=True, blank=True
    )

    country = models.CharField(
        max_length=100,
        null=True,
        blank=True)  # Change from CountryField to CharField
    region = models.CharField(max_length=100, null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True
    )


class Election(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    active_from = models.DateTimeField(null=True, blank=True)
    total_voters = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def calculate_total_voters(self):
        return self.vote_set.values('user').distinct().count()


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
