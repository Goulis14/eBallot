from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),  # This will load index.html
    # path('election/<int:election_id>/', views.election_detail, name='election_detail'),
    # path('election/<int:election_id>/results/', views.results, name='results'),
]