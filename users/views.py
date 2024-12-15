from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm

# Register View
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user to the database.
            login(request, user)  # Log the user in immediately after registration.
            return redirect('election_list')  # Redirect to the election list (or any page of your choice).
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()  # Get the authenticated user.
            login(request, user)  # Log the user in.
            return redirect('election_list')  # Redirect to the election list.
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)  # Log the user out.
    return redirect('login')  # Redirect to the login page.