from django.contrib import admin
from .models import Candidate


# Register your models here.
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'election')  # Εμφάνιση ονόματος και ψηφοφορίας.
    list_filter = ('election',)  # Φιλτράρισμα με βάση την ψηφοφορία.
    search_fields = ('name', 'election__title')  # Αναζήτηση με βάση το όνομα και την ψηφοφορία.
