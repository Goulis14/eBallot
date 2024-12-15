from django.conf import settings
from django.db import models


# Create your models here.

class Election(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)  # Για ενεργές/ανενεργές ψηφοφορίες.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Συνδέεται με το custom ή default User model.
        on_delete=models.CASCADE,  # Διαγράφεται η ψηφοφορία αν διαγραφεί ο δημιουργός.
        related_name='created_elections'  # Εύχρηστο όνομα για πρόσβαση στις εκλογές ενός χρήστη.
    )

    def __str__(self):
        return self.title
