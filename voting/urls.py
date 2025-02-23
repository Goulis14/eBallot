# voting/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),  # This will load index.html
    path('signup/', views.sign_up, name='sign_up'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),  # Add this line for the profile page
    path('create_election/', views.create_election, name='create_election'),
    path('election/<int:election_id>/', views.election_detail, name='election_detail'),  # View election and vote
    path('election/results/<int:election_id>/', views.results, name='results'),

    # Election List Page
    path('elections/', views.election_list, name='election_list'),  # List active elections

    # Mount FastAPI routes
    path('get-countries/', views.get_countries, name='get_countries'),
    path('get-regions/', views.get_regions, name='get_regions'),
]
