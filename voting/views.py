# voting/views.py
import logging
import os
import json
from django.http import JsonResponse
from django.conf import settings
import openai
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
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            # Save the new user
            user = form.save()
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            # Authenticate and log the user in
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                messages.success(request, "Your account has been created and you're now logged in.")
                return redirect('home')  # Redirect to home or other page
            else:
                messages.error(request, "There was an issue logging you in after signup.")
        else:
            messages.error(request, "There were errors with your signup form.")
            print(form.errors)
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


def results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = Candidate.objects.filter(election=election)

    total_votes = Vote.objects.filter(election=election).count()
    total_voters = election.total_voters
    votes_cast = Vote.objects.filter(election=election).values('user').distinct().count()

    turnout_percentage = (votes_cast / total_voters * 100) if total_voters else 0

    candidate_results = candidates.annotate(vote_count=Count('vote'))

    results = []
    votes_json = {'labels': [], 'values': []}

    for candidate in candidate_results:
        percentage = (candidate.vote_count / total_votes * 100) if total_votes > 0 else 0
        results.append({
            'name': candidate.name,
            'votes': candidate.vote_count,
            'percentage': percentage,
        })
        votes_json['labels'].append(candidate.name)
        votes_json['values'].append(percentage)

    # Age Group Demographics
    age_demographics = models.CustomUser.objects.filter(
        vote__election=election
    ).values('age_group').annotate(count=Count('id'))

    age_demographics_data = [{'age_group': d['age_group'], 'count': d['count']} for d in age_demographics]

    # Gender Demographics
    gender_demographics = models.CustomUser.objects.filter(
        vote__election=election
    ).values('gender').annotate(count=Count('id'))

    gender_demographics_data = [{'gender': d['gender'], 'count': d['count']} for d in gender_demographics]

    # Country Demographics
    country_demographics = models.CustomUser.objects.filter(
        vote__election=election
    ).values('country').annotate(count=Count('id'))

    country_demographics_data = [{'country': d['country'], 'count': d['count']} for d in country_demographics]

    # Compute how each group voted
    # Gender Vote Summary
    gender_vote_summary = Vote.objects.filter(election=election) \
        .values("user__gender", "candidate__name") \
        .annotate(votes=Count("id"))

    country_vote_summary = Vote.objects.filter(election=election) \
        .values("user__country", "candidate__name") \
        .annotate(votes=Count("id"))

    age_vote_summary = Vote.objects.filter(election=election) \
        .values("user__age_group", "candidate__name") \
        .annotate(votes=Count("id"))

    # Aggregate gender vote data for each gender
    gender_summary = {}
    for entry in gender_vote_summary:
        gender = entry['user__gender']
        candidate = entry['candidate__name']
        votes = entry['votes']

        if gender not in gender_summary:
            gender_summary[gender] = {}

        gender_summary[gender][candidate] = votes

    print(gender_vote_summary)
    return render(request, 'voting/results.html', {
        'election': election,
        'results': results,
        'total_votes': total_votes,
        'total_voters': total_voters,
        'turnout_percentage': turnout_percentage,
        'age_demographics': age_demographics_data,
        'gender_demographics': gender_demographics_data,
        'country_demographics': country_demographics_data,
        'gender_vote_summary': gender_vote_summary,
        'country_vote_summary': country_vote_summary,
        'age_vote_summary': age_vote_summary,
        'gender_summary': gender_summary,
    })


def results_api(request, election_id):
    election = Election.objects.get(id=election_id)
    candidates = Candidate.objects.filter(election=election)

    total_votes = Vote.objects.filter(election=election).count()
    candidate_results = candidates.annotate(vote_count=Count('vote'))

    results = []
    for candidate in candidate_results:
        percentage = (candidate.vote_count / total_votes * 100) if total_votes > 0 else 0
        results.append({
            'name': candidate.name,
            'votes': candidate.vote_count,
            'percentage': round(percentage, 2)
        })

    data = {
        'election': election.name,
        'total_votes': total_votes,
        'results': results,
    }

    return JsonResponse(data)

# Function to read countries and states data from the JSON file


# Function to read countries and states data from the JSON file
def get_countries(request):
    json_path = os.path.join(settings.BASE_DIR,
                             'static/data/countries+states.json')  # Path to your countries+states.json file

    try:
        # Open and read the countries+states JSON file
        with open(json_path, "r", encoding="utf-8") as json_file:
            countries_data = json.load(json_file)

        # Prepare a list of countries to return in the response
        countries_list = [{"name": country["name"], "iso2": country["iso2"]} for country in countries_data]

        return JsonResponse({"countries": countries_list}, safe=False)  # Return countries as JSON

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)  # Handle errors


def get_regions(request):
    country_name = request.GET.get('country_name', None)

    if not country_name:
        return JsonResponse({"error": "Country name is required"}, status=400)

    json_path = os.path.join(settings.BASE_DIR, 'static/data/countries+states.json')

    try:
        with open(json_path, "r", encoding="utf-8") as json_file:
            countries_data = json.load(json_file)

        # Find the regions of the selected country
        for country in countries_data:
            if country["name"] == country_name:
                regions_list = [{"name": region["name"]} for region in country.get("states", [])]
                return JsonResponse({"regions": regions_list}, safe=False)

        return JsonResponse({"error": "Country not found"}, status=404)  # Country not found

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def generate_ai_summary(election, candidate_results, total_votes):
    openai.api_key = settings.OPENAI_API_KEY

    winner = max(candidate_results, key=lambda c: c.votes).name if candidate_results else "No Winner"
    close_race = any(c.votes == candidate_results[0].votes for c in candidate_results[1:]) if len(
        candidate_results) > 1 else False

    prompt = f"""
    Election Title: {election.title}
    Total Votes: {total_votes}
    Winner: {winner}
    Candidates and Votes:
    {''.join(f'{c.name}: {c.votes} votes ({c.vote_percentage:.2f}%)\n' for c in candidate_results)}

    Write a short summary of the election result. Mention if the election was close, the winner, and highlight the voter turnout.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Free tier model
            messages=[{"role": "system", "content": "You are a voting results analyst."},
                      {"role": "user", "content": prompt}],
            max_tokens=150
        )
        summary = response['choices'][0]['message']['content'].strip()
        return summary
    except Exception as e:
        return "AI analysis is currently unavailable."
