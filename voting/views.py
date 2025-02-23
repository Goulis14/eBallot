# voting/views.py
import logging
from django.conf import settings
import os
import json
from django.http import JsonResponse
import requests
from django_countries import countries
from django.contrib.messages import get_messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from .forms import SignUpForm, ElectionForm, CandidateFormSet
from . import models
from .models import Election, Candidate, Vote
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone


# Αρχική Σελίδα - Λίστα Ψηφοφοριών
def index(request):
    return render(request, 'voting/home.html')


# Σελίδα Ψηφοφορίας - Προβολή και Ψήφος
@login_required
def election_detail(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        candidate = get_object_or_404(Candidate, id=candidate_id)
        Vote.objects.create(user=request.user, election=election, candidate=candidate)
        return redirect('results', election_id=election.id)
    return render(request, 'voting/election_detail.html', {'election': election})


def sign_up(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home if already logged in

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            # Save the user and create it in the database
            user = form.save()

            # Authenticate the user after saving
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)

            if user is not None:
                # Log the user in
                login(request, user)

                # Show success message
                messages.success(request, "Your account has been created and you're now logged in.")

                # Redirect to the home page
                return redirect('home')
            else:
                # Log the error if the user couldn't be authenticated
                messages.error(request, "There was an issue logging you in after signup.")
                print(f"Authentication failed for user: {username}")
        else:
            # If the form isn't valid, print the errors for debugging
            print(form.errors)  # Print form errors to check validation issues
            messages.error(request, "There were errors with your signup form.")

    else:
        form = SignUpForm()

    return render(request, 'voting/sign_up.html', {'form': form})


# Login View (Django built-in)
class CustomLoginView(LoginView):
    template_name = 'voting/login.html'  # Custom login page
    success_url = '/'  # Redirect to the homepage after login


# Logout View (Django built-in)
class CustomLogoutView(LogoutView):
    next_page = 'home'  # Redirect to home page after logout


# Profile Page
@login_required
def profile(request):
    return render(request, 'voting/profile.html')


# View for listing all active elections

logger = logging.getLogger(__name__)


def home(request):
    current_time = timezone.now()
    print(f"Current time: {current_time}")

    active_elections = Election.objects.filter(
        start_date__lte=current_time,
        end_date__gte=current_time,
        is_active=True
    )

    print(f"Active Elections in View: {active_elections.count()}")
    for e in active_elections:
        print(
            f"Election in View - ID: {e.id}, Title: {e.title}, Start Date: {e.start_date}, End Date: {e.end_date}, Active: {e.is_active}")

    return render(request, 'voting/home.html', {'active_elections': active_elections})


@login_required
def election_detail(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    # Clear old messages to prevent duplicates
    storage = get_messages(request)
    for _ in storage:
        pass  # This ensures previous messages are cleared

    # Check if the user has already voted
    if Vote.objects.filter(user=request.user, election=election).exists():
        messages.info(request, "You have already voted in this election. Redirecting to results.")
        return redirect('results', election_id=election.id)  # Redirect to results page

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        candidate = get_object_or_404(Candidate, id=candidate_id)
        Vote.objects.create(user=request.user, election=election, candidate=candidate)
        messages.success(request, "Your vote has been recorded! Redirecting to results.")
        return redirect('results', election_id=election.id)

    # Fetch all candidates for the election
    candidates = election.candidates.all()
    return render(request, 'voting/election_detail.html', {'election': election, 'candidates': candidates})


# Only Admins can create an election
@login_required
def create_election(request):
    if request.user.role != 'Admin':
        messages.error(request, "You do not have permission to create elections.")
        return redirect('home')

    if request.method == 'POST':
        form = ElectionForm(request.POST)
        formset = CandidateFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            election = form.save(commit=False)
            election.created_by = request.user
            election.save()
            formset.instance = election
            formset.save()
            messages.success(request, "Election and candidates created successfully!")
            return redirect('home')
        else:
            messages.error(request, "There was an issue creating the election. Please fix the errors below.")
    else:
        form = ElectionForm()
        formset = CandidateFormSet()

    return render(request, 'voting/create_election.html', {
        'form': form,
        'formset': formset,
        'empty_form': formset.empty_form.as_p()  # Include empty form for JavaScript
    })


# View for listing all active elections
@login_required
def election_list(request):
    # Fetch active elections
    active_elections = Election.objects.filter(is_active=True)

    # If there are no active elections, display a message
    if not active_elections:
        messages.info(request, "No active elections at the moment.")

    return render(request, 'voting/election_list.html', {'active_elections': active_elections})


@login_required
def results(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    # Count votes for each candidate
    candidate_results = Candidate.objects.filter(election=election).annotate(votes=Count('vote'))

    # Calculate the total number of votes
    total_votes = candidate_results.aggregate(total_votes=Sum('votes'))['total_votes'] or 0

    # Calculate the percentage of total votes for each candidate
    for candidate in candidate_results:
        candidate.vote_percentage = (candidate.votes / total_votes * 100) if total_votes > 0 else 0

    return render(request, 'voting/results.html',
                  {'election': election, 'candidate_results': candidate_results, 'total_votes': total_votes})


# Function to read countries and states data from the JSON file
# Load countries from the JSON file
def get_countries(request):
    json_path = os.path.join(settings.BASE_DIR, 'static/data/countries+states.json')

    try:
        with open(json_path, encoding="utf-8") as json_file:
            countries_data = json.load(json_file)

        countries_list = [{"name": country["name"], "iso2": country["iso2"]} for country in countries_data]
        return JsonResponse({"countries": countries_list}, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Fetch countries list
def get_regions(request):
    country_iso2 = request.GET.get('country_iso2', None)

    if not country_iso2:
        return JsonResponse({"error": "Country code is required"}, status=400)

    json_path = os.path.join(settings.BASE_DIR, 'static/data/countries+states.json')

    try:
        with open(json_path, encoding="utf-8") as json_file:
            countries_data = json.load(json_file)

        for country in countries_data:
            if country["iso2"] == country_iso2:
                regions_list = [{"id": region["id"], "name": region["name"]} for region in country.get("states", [])]
                return JsonResponse({"regions": regions_list}, safe=False)

        return JsonResponse({"error": "Country not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)