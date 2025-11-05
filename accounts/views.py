from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('campsites_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('campsites_list')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    # Add Tailwind classes to form fields
    for field in form.fields.values():
        field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
    
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('campsites_list')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcome to Euro Camp, {username}!')
            login(request, user)
            return redirect('campsites_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')
