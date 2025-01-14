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
    path('election/<int:election_id>/results/', views.results, name='results'),  # View election results

    # Election List Page
    path('elections/', views.election_list, name='election_list'),  # List active elections
]
