from django.urls import path
from . import views  # Import the views for vote-related actions

urlpatterns = [
    path('list/', views.vote_list, name='vote_list'),
    path('detail/<int:id>/', views.vote_detail, name='vote_detail'),
]