from django.db import models
from elections.models import Election


# Create your models here.
class Candidate(models.Model):
    name = models.CharField(max_length=255)  # Όνομα υποψηφίου.
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,  # Διαγραφή υποψηφίων αν διαγραφεί η ψηφοφορία.
        related_name='candidates'  # Εύκολη πρόσβαση στους υποψήφιους μέσω Election.
    )

    def __str__(self):
        return f"{self.name} ({self.election.title})"
