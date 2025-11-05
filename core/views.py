from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Campsite
from .forms import CampsiteForm


def home(request):
    """Render the home page."""
    return render(request, 'home.html')


@login_required
def campsites_list(request):
    """Display list of all campsites."""
    campsites = Campsite.objects.all()
    can_modify = request.user.is_superuser or request.user.groups.filter(name='Campsite Managers').exists()
    return render(request, 'campsites/list.html', {'campsites': campsites, 'can_modify': can_modify})


@login_required
def campsite_detail(request, pk):
    """Display details of a specific campsite."""
    campsite = get_object_or_404(Campsite, pk=pk)
    # Check if user can edit/delete
    can_modify = request.user.is_superuser or request.user.groups.filter(name='Campsite Managers').exists()
    return render(request, 'campsites/detail.html', {'campsite': campsite, 'can_modify': can_modify})


@login_required
def campsite_create(request):
    """Create a new campsite (superusers and Campsite Managers only)."""
    # Check permissions
    if not (request.user.is_superuser or request.user.groups.filter(name='Campsite Managers').exists()):
        return HttpResponseForbidden("You don't have permission to create campsites.")
    
    if request.method == 'POST':
        form = CampsiteForm(request.POST)
        if form.is_valid():
            campsite = form.save()
            messages.success(request, f'{campsite.name} has been created successfully!')
            return redirect('campsite_detail', pk=campsite.pk)
    else:
        form = CampsiteForm()
    
    return render(request, 'campsites/create.html', {'form': form})


@login_required
def campsite_edit(request, pk):
    """Edit a campsite (superusers and Campsite Managers only)."""
    campsite = get_object_or_404(Campsite, pk=pk)
    
    # Check permissions
    if not (request.user.is_superuser or request.user.groups.filter(name='Campsite Managers').exists()):
        return HttpResponseForbidden("You don't have permission to edit campsites.")
    
    if request.method == 'POST':
        form = CampsiteForm(request.POST, instance=campsite)
        if form.is_valid():
            form.save()
            messages.success(request, f'{campsite.name} has been updated successfully!')
            return redirect('campsite_detail', pk=campsite.pk)
    else:
        form = CampsiteForm(instance=campsite)
    
    return render(request, 'campsites/edit.html', {'form': form, 'campsite': campsite})


@login_required
def campsite_delete(request, pk):
    """Delete a campsite (superusers and Campsite Managers only)."""
    campsite = get_object_or_404(Campsite, pk=pk)
    
    # Check permissions
    if not (request.user.is_superuser or request.user.groups.filter(name='Campsite Managers').exists()):
        return HttpResponseForbidden("You don't have permission to delete campsites.")
    
    if request.method == 'POST':
        campsite_name = campsite.name
        campsite.delete()
        messages.success(request, f'{campsite_name} has been deleted successfully!')
        return redirect('campsites_list')
    
    return render(request, 'campsites/delete.html', {'campsite': campsite})
