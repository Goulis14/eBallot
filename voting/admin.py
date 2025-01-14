from django.contrib import admin
from .models import CustomUser, Election, Candidate, Vote


# Register your models here.
# Εγγραφή του CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


# Εγγραφή του Election
@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'created_by')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')


# Εγγραφή του Candidate
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'election')
    list_filter = ('election',)
    search_fields = ('name',)


# Εγγραφή του Vote
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'election', 'candidate', 'timestamp')
    list_filter = ('election', 'timestamp')
    search_fields = ('user__username', 'candidate__name')
