from django.contrib import admin
from .models import Vote  # Import the Vote model from models.py


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'election', 'candidate', 'timestamp')
    list_filter = ('election', 'candidate', 'timestamp')
    search_fields = ('user__username', 'election__title', 'candidate__name')
