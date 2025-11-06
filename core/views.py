from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Campsite
from .forms import CampsiteForm


def home(request):
    """Render the home page."""
    # Get the last two campsites ordered by creation date
    recent_campsites = Campsite.objects.order_by('-created_at')[:2]
    return render(request, 'home.html', {'recent_campsites': recent_campsites})


@login_required
def campsites_list(request):
    """Display list of all campsites."""
    campsites = Campsite.objects.all()
    # Can add new campsites if superuser or in CampsiteManager group
    can_add = request.user.is_superuser or request.user.groups.filter(name='CampsiteManager').exists()
    return render(request, 'campsites/list.html', {'campsites': campsites, 'can_modify': can_add})


@login_required
def campsite_detail(request, pk):
    """Display details of a specific campsite."""
    campsite = get_object_or_404(Campsite, pk=pk)
    # Check if user can edit/delete: superuser can modify any, CampsiteManager can only modify their own
    can_modify = request.user.is_superuser or (request.user.groups.filter(name='CampsiteManager').exists() and campsite.created_by == request.user)
    return render(request, 'campsites/detail.html', {'campsite': campsite, 'can_modify': can_modify})


@login_required
def campsite_create(request):
    """Create a new campsite (superusers and CampsiteManager group only)."""
    # Check permissions
    if not (request.user.is_superuser or request.user.groups.filter(name='CampsiteManager').exists()):
        return HttpResponseForbidden("You don't have permission to create campsites.")
    
    if request.method == 'POST':
        form = CampsiteForm(request.POST)
        if form.is_valid():
            campsite = form.save(commit=False)
            campsite.created_by = request.user
            campsite.save()
            messages.success(request, f'{campsite.name} has been created successfully!')
            return redirect('campsite_detail', pk=campsite.pk)
    else:
        form = CampsiteForm()
    
    return render(request, 'campsites/create.html', {'form': form})


@login_required
def campsite_edit(request, pk):
    """Edit a campsite (superusers can edit any, CampsiteManager can only edit their own)."""
    campsite = get_object_or_404(Campsite, pk=pk)
    
    # Check permissions: superuser can edit any, CampsiteManager can only edit their own
    if not request.user.is_superuser:
        if not (request.user.groups.filter(name='CampsiteManager').exists() and campsite.created_by == request.user):
            return HttpResponseForbidden("You don't have permission to edit this campsite.")
    
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
    """Delete a campsite (superusers can delete any, CampsiteManager can only delete their own)."""
    campsite = get_object_or_404(Campsite, pk=pk)
    
    # Check permissions: superuser can delete any, CampsiteManager can only delete their own
    if not request.user.is_superuser:
        if not (request.user.groups.filter(name='CampsiteManager').exists() and campsite.created_by == request.user):
            return HttpResponseForbidden("You don't have permission to delete this campsite.")
    
    if request.method == 'POST':
        campsite_name = campsite.name
        campsite.delete()
        messages.success(request, f'{campsite_name} has been deleted successfully!')
        return redirect('campsites_list')
    
    return render(request, 'campsites/delete.html', {'campsite': campsite})
