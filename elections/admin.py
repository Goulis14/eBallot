from django.contrib import admin
from .models import Election
from candidates.models import Candidate


# Register your models here.

class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1  # Αριθμός κελιών για νέες εγγραφές.


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'created_by')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'created_by__username')
