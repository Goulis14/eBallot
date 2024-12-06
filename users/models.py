from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    # Δημιουργία πεδίου για τον ρόλο του χρήστη
    role = models.CharField(
        max_length=20,
        choices=[('Admin', 'Admin'), ('Voter', 'Voter')],
        default='Voter'
    )

    # Μέθοδος για την αναπαράσταση του χρήστη ως κείμενο
    def __str__(self):
        return self.username
