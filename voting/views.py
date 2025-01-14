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


# Σελίδα Αποτελεσμάτων
@login_required
def results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    results = election.candidates.annotate(votes=models.Count('vote'))

    total_votes = results.aggregate(total_votes=models.Sum('votes'))['total_votes'] or 0

    # Calculate the percentage of total votes for each candidate
    for candidate in results:
        candidate.vote_percentage = (candidate.votes / total_votes * 100) if total_votes > 0 else 0

    return render(request, 'voting/results.html', {'election': election, 'results': results})


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
@login_required
def home(request):
    active_elections = Election.objects.filter(is_active=True)
    print(active_elections)  # Should print the list of active elections
    return render(request, 'voting/home.html', {'active_elections': active_elections})


@login_required
def election_detail(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    # Check if the user has already voted in this election
    if Vote.objects.filter(user=request.user, election=election).exists():
        messages.info(request, "You have already voted in this election.")
        return redirect('results', election_id=election.id)

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        candidate = get_object_or_404(Candidate, id=candidate_id)
        Vote.objects.create(user=request.user, election=election, candidate=candidate)
        return redirect('results', election_id=election.id)

    # Fetch all candidates for the election
    candidates = election.candidates.all()
    return render(request, 'voting/election_detail.html', {'election': election, 'candidates': candidates})


# Only Admins can create an election
@login_required
def create_election(request):
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        formset = CandidateFormSet(request.POST)  # Bind the inline formset to the POST data

        if form.is_valid() and formset.is_valid():
            # Save the election and associate it with the logged-in user
            election = form.save(commit=False)
            election.created_by = request.user
            election.save()

            # Save the candidates, associating them with the election
            formset.instance = election
            formset.save()

            # Show success message and redirect
            messages.success(request, "Election and candidates created successfully!")
            return redirect('home')
        else:
            # If either form or formset isn't valid, show error messages
            messages.error(request, "There was an issue creating the election. Please fix the errors below.")
    else:
        form = ElectionForm()
        formset = CandidateFormSet()

    return render(request, 'voting/create_election.html', {
        'form': form,
        'formset': formset,
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