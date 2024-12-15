from django.shortcuts import render, get_object_or_404
from .models import Vote  # Import the Vote model

# View to display all votes
def vote_list(request):
    votes = Vote.objects.all()  # Get all votes from the database
    return render(request, 'votes/vote_list.html', {'votes': votes})

# View to display details of a specific vote
def vote_detail(request, id):
    vote = get_object_or_404(Vote, id=id)  # Get the vote by id, or 404 if not found
    return render(request, 'votes/vote_detail.html', {'vote': vote})
