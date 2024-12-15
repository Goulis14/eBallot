from django.shortcuts import render, get_object_or_404
from .models import Election


# View for displaying all elections
def election_list(request):
    elections = Election.objects.all()  # Get all elections
    return render(request, 'elections/election_list.html', {'elections': elections})


# View for displaying a specific election's details
def election_detail(request, id):
    election = get_object_or_404(Election, id=id)  # Get election by id or return 404 if not found
    return render(request, 'elections/election_detail.html', {'election': election})
