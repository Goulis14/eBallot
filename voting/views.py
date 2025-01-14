from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from . import models
from .models import Election, Candidate, Vote


# Αρχική Σελίδα - Λίστα Ψηφοφοριών
def index(request):
    return render(request, 'voting/index.html')


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
    return render(request, 'voting/results.html', {'election': election, 'results': results})
