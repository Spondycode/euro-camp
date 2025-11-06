from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.db.models import Count
from .models import Campsite, CampsiteLike
from .forms import CampsiteForm
from .utils import upload_campsite_image


def home(request):
    """Render the home page."""
    # Get the last two approved campsites ordered by creation date
    # Staff can see all; others only see approved
    if request.user.is_authenticated and request.user.is_staff:
        recent_campsites = Campsite.objects.order_by('-created_at')[:2]
    else:
        recent_campsites = Campsite.objects.filter(is_approved=True).order_by('-created_at')[:2]
    return render(request, 'home.html', {'recent_campsites': recent_campsites})


@login_required
def campsites_list(request):
    """Display list of all campsites."""
    # Staff can see all campsites; others only see approved
    if request.user.is_staff:
        all_campsites = Campsite.objects.all()
    else:
        all_campsites = Campsite.objects.filter(is_approved=True)
    
    # Annotate with like counts
    all_campsites = all_campsites.annotate(like_count=Count('likes'))
    
    # Separate premium and regular campsites
    premium_campsites = all_campsites.filter(is_premium=True)
    regular_campsites = all_campsites.filter(is_premium=False)
    
    # Get current user's liked campsite IDs
    liked_campsite_ids = set()
    if request.user.is_authenticated:
        liked_campsite_ids = set(
            CampsiteLike.objects.filter(user=request.user).values_list('campsite_id', flat=True)
        )
    
    # Can add new campsites if superuser or in CampsiteManager group
    can_add = request.user.is_superuser or request.user.groups.filter(name='CampsiteManager').exists()
    
    return render(request, 'campsites/list.html', {
        'premium_campsites': premium_campsites,
        'campsites': regular_campsites,
        'can_modify': can_add,
        'liked_campsite_ids': liked_campsite_ids
    })


@login_required
def campsite_detail(request, pk):
    """Display details of a specific campsite."""
    campsite = get_object_or_404(
        Campsite.objects.annotate(like_count=Count('likes')),
        pk=pk
    )
    
    # Check if user can view: approved, staff, or the suggester themselves
    if not campsite.is_approved:
        if not (request.user.is_staff or campsite.suggested_by == request.user):
            raise PermissionDenied("You don't have permission to view this campsite.")
    
    # Get current user's liked campsite IDs
    liked_campsite_ids = set()
    if request.user.is_authenticated:
        liked_campsite_ids = set(
            CampsiteLike.objects.filter(user=request.user).values_list('campsite_id', flat=True)
        )
    
    # Check if user can edit/delete: superuser can modify any, CampsiteManager can only modify their own
    can_modify = request.user.is_superuser or (request.user.groups.filter(name='CampsiteManager').exists() and campsite.created_by == request.user)
    return render(request, 'campsites/detail.html', {
        'campsite': campsite,
        'can_modify': can_modify,
        'liked_campsite_ids': liked_campsite_ids
    })


@login_required
def campsite_create(request):
    """Create a new campsite (superusers and CampsiteManager group only)."""
    # Check permissions
    if not (request.user.is_superuser or request.user.groups.filter(name='CampsiteManager').exists()):
        return HttpResponseForbidden("You don't have permission to create campsites.")
    
    if request.method == 'POST':
        form = CampsiteForm(request.POST, request.FILES)
        if form.is_valid():
            campsite = form.save(commit=False)
            campsite.created_by = request.user
            
            # Handle image upload
            uploaded_image = form.cleaned_data.get('image')
            if uploaded_image:
                try:
                    campsite.image_url = upload_campsite_image(uploaded_image)
                except Exception as e:
                    messages.error(request, f'Image upload failed: {e}')
            
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
        form = CampsiteForm(request.POST, request.FILES, instance=campsite)
        if form.is_valid():
            campsite = form.save(commit=False)
            
            # Handle image upload
            uploaded_image = form.cleaned_data.get('image')
            if uploaded_image:
                try:
                    campsite.image_url = upload_campsite_image(uploaded_image)
                except Exception as e:
                    messages.error(request, f'Image upload failed: {e}')
            
            campsite.save()
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


@login_required
def campsite_suggest(request):
    """Allow any authenticated user to suggest a campsite."""
    if request.method == 'POST':
        form = CampsiteForm(request.POST, request.FILES)
        if form.is_valid():
            campsite = form.save(commit=False)
            campsite.suggested_by = request.user
            
            # Auto-approve if user has 3+ approved suggestions or is staff
            campsite.is_approved = request.user.can_auto_approve_campsites or request.user.is_staff
            
            # Handle image upload
            uploaded_image = form.cleaned_data.get('image')
            if uploaded_image:
                try:
                    campsite.image_url = upload_campsite_image(uploaded_image)
                except Exception as e:
                    messages.error(request, f'Image upload failed: {e}')
            
            campsite.save()
            
            if campsite.is_approved:
                messages.success(request, f'{campsite.name} was auto-approved and is now live!')
            else:
                messages.success(request, f'{campsite.name} has been submitted and is pending review.')
            
            return redirect('campsite_detail', pk=campsite.pk)
    else:
        form = CampsiteForm()
    
    return render(request, 'campsites/suggest.html', {'form': form})


@login_required
def my_suggestions(request):
    """Display user's suggested campsites and liked campsites."""
    suggestions = Campsite.objects.filter(suggested_by=request.user).order_by('-created_at')
    
    # Get campsites the user has liked
    liked_campsites = Campsite.objects.filter(
        likes__user=request.user,
        is_approved=True
    ).annotate(like_count=Count('likes')).order_by('-likes__created_at')
    
    return render(request, 'campsites/my_suggestions.html', {
        'suggestions': suggestions,
        'liked_campsites': liked_campsites
    })


@staff_member_required
def pending_campsites(request):
    """Display pending campsite suggestions (staff only)."""
    pending = Campsite.objects.filter(is_approved=False).select_related('suggested_by').order_by('created_at')
    return render(request, 'campsites/pending.html', {'pending_campsites': pending})


@staff_member_required
def admin_manage_suggestions(request):
    """Admin page to manage pending campsite suggestions with toggle approval."""
    # Get only pending (unapproved) campsites ordered by creation date
    campsites = Campsite.objects.filter(is_approved=False).select_related('suggested_by').order_by('-created_at')
    return render(request, 'campsites/admin_manage.html', {'campsites': campsites})


@staff_member_required
@require_POST
def toggle_campsite_approval(request, pk):
    """Toggle approval status of a campsite via AJAX."""
    campsite = get_object_or_404(Campsite, pk=pk)
    campsite.is_approved = not campsite.is_approved
    campsite.save()
    
    return JsonResponse({
        'success': True,
        'is_approved': campsite.is_approved,
        'message': f'{campsite.name} has been {"approved" if campsite.is_approved else "unapproved"}.'
    })
