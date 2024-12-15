from django.shortcuts import render, get_object_or_404
from .models import Candidate  # Import the Candidate model

# View to display all candidates
def candidate_list(request):
    candidates = Candidate.objects.all()  # Get all candidates from the database
    return render(request, 'candidates/candidate_list.html', {'candidates': candidates})

# View to display details of a specific candidate
def candidate_detail(request, id):
    candidate = get_object_or_404(Candidate, id=id)  # Get the candidate by id, or 404 if not found
    return render(request, 'candidates/candidate_detail.html', {'candidate': candidate})
