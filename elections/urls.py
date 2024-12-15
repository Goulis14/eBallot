from django.urls import path
from . import views  # Import views for election-related actions

urlpatterns = [
    # Add your election-related paths here, for example:
    path('list/', views.election_list, name='election_list'),
    path('detail/<int:id>/', views.election_detail, name='election_detail'),
]