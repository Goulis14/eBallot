from django.urls import path
from . import views  # Import views for candidate-related actions

urlpatterns = [
    # Add your candidate-related paths here
    path('list/', views.candidate_list, name='candidate_list'),
    path('detail/<int:id>/', views.candidate_detail, name='candidate_detail'),
]