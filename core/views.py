import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.urls import reverse
from .models import Campsite, CampsiteLike, Product
from .forms import CampsiteForm, ProductForm
from .utils import upload_campsite_image, upload_product_image, parse_lat_lng, get_campsites_within_radius


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
    """Display list of all campsites with pagination."""
    from django.core.paginator import Paginator
    
    user = request.user
    
    # Staff can see all campsites; others only see approved
    qs = Campsite.objects.all()
    if not user.is_staff:
        qs = qs.filter(is_approved=True)
    
    # Annotate with like counts and order: premium first, then by like count, then by name
    qs = qs.annotate(
        like_count=Count('likes', distinct=True)
    ).order_by('-is_premium', '-like_count', 'name')
    
    # Paginate with first 30 items
    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(1)
    
    # Get current user's liked campsite IDs
    liked_campsite_ids = set()
    if user.is_authenticated:
        liked_campsite_ids = set(
            CampsiteLike.objects.filter(user=user).values_list('campsite_id', flat=True)
        )
    
    # Can add new campsites if superuser or in CampsiteManager group
    can_add = user.is_superuser or user.groups.filter(name='CampsiteManager').exists()
    
    return render(request, 'campsites/list.html', {
        'campsites': page_obj.object_list,
        'pagination_meta': {
            'count': paginator.count,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'next_page': 2 if paginator.num_pages > 1 else None,
        },
        'initial_filters': {
            'country': request.GET.get('country', ''),
            'search': request.GET.get('search', ''),
        },
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


@login_required
def campsites_map(request):
    """Display campsites on an interactive map with two modes: country view or radius view."""
    country_param = request.GET.get("country")
    campsite_id_param = request.GET.get("campsite_id")

    # Base queryset respecting approval rules
    base_qs = Campsite.objects.all()
    if not request.user.is_staff:
        base_qs = base_qs.filter(is_approved=True)

    # Annotate like counts
    base_qs = base_qs.annotate(like_count=Count("likes", distinct=True))

    # Get distinct countries for dropdown
    countries = (
        base_qs.exclude(country__isnull=True)
               .exclude(country__exact="")
               .values_list("country", flat=True)
               .distinct()
               .order_by("country")
    )

    mode = "country"
    radius_km = 100
    center_campsite = None
    campsites_qs = base_qs

    # Determine mode and filter campsites
    if campsite_id_param:
        mode = "radius"
        center_campsite = get_object_or_404(base_qs, pk=campsite_id_param)
        campsites_qs = get_campsites_within_radius(center_campsite, radius_km, base_qs)
        # Re-apply like count annotation after radius filtering
        campsites_qs = campsites_qs.annotate(like_count=Count("likes", distinct=True))
    elif country_param:
        mode = "country"
        campsites_qs = base_qs.filter(country__iexact=country_param)
    else:
        mode = "country"

    # Prepare marker data; skip invalid coords
    campsite_points = []
    for cs in campsites_qs:
        coords = parse_lat_lng(cs)
        if not coords:
            continue
        lat, lng = coords
        campsite_points.append({
            "id": cs.pk,
            "name": cs.name,
            "country": cs.get_country_display() if hasattr(cs, 'get_country_display') else cs.country,
            "lat": lat,
            "lng": lng,
            "likes": cs.like_count,
            "url": reverse("campsite_detail", args=[cs.pk]),
        })

    # Determine map center
    center_lat, center_lng = 54.5260, 15.2551  # Europe fallback
    if mode == "radius" and center_campsite:
        c = parse_lat_lng(center_campsite)
        if c:
            center_lat, center_lng = c
    elif campsite_points:
        # Calculate centroid of available points
        center_lat = sum(p["lat"] for p in campsite_points) / len(campsite_points)
        center_lng = sum(p["lng"] for p in campsite_points) / len(campsite_points)

    # Build title and back URL
    count = len(campsite_points)
    if mode == "radius" and center_campsite:
        title = f"Campsites within {radius_km} km of {center_campsite.name}"
        back_url = reverse("campsite_detail", args=[center_campsite.pk])
    else:
        if country_param:
            # Get the full country name for display
            country_display = dict(Campsite.COUNTRY_CHOICES).get(country_param, country_param)
            title = f"Campsites in {country_display}"
        else:
            title = "All Campsites"
        back_url = reverse("campsites_list")

    # Build map config payload
    map_config = {
        "mode": mode,
        "radius_km": radius_km,
        "center": {"lat": center_lat, "lng": center_lng},
        "centerCampsite": (
            {"id": center_campsite.pk, "name": center_campsite.name}
            if center_campsite else None
        ),
        "selectedCountry": country_param,
        "campsites": campsite_points,
        "tile": {
            "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "attribution": "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
        },
    }

    context = {
        "title": title,
        "count": count,
        "countries": countries,
        "selected_country": country_param,
        "back_url": back_url,
        "map_config_json": json.dumps(map_config),
        "mode": mode,
    }
    return render(request, "campsites/map.html", context)


# Product Views

@login_required
def products_list(request):
    """Display list of featured camping products."""
    products = Product.objects.filter(is_featured=True).order_by('name')
    
    # Check if user is super admin
    can_modify = request.user.is_super_admin or request.user.is_superuser
    
    return render(request, 'products/list.html', {
        'products': products,
        'can_modify': can_modify
    })


@login_required
def product_detail(request, pk):
    """Display details of a specific product."""
    product = get_object_or_404(Product, pk=pk)
    
    # Check if user can modify (super admin only)
    can_modify = request.user.is_super_admin or request.user.is_superuser
    
    return render(request, 'products/detail.html', {
        'product': product,
        'can_modify': can_modify
    })


@login_required
def product_create(request):
    """Create a new product (super admins only)."""
    # Check permissions
    if not (request.user.is_super_admin or request.user.is_superuser):
        return HttpResponseForbidden("You don't have permission to create products.")
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            
            # Handle image upload
            uploaded_image = form.cleaned_data.get('image')
            if uploaded_image:
                try:
                    product.image_url = upload_product_image(uploaded_image)
                except Exception as e:
                    messages.error(request, f'Image upload failed: {e}')
            
            product.save()
            messages.success(request, f'{product.name} has been created successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    
    return render(request, 'products/create.html', {'form': form})


@login_required
def product_edit(request, pk):
    """Edit a product (super admins only)."""
    product = get_object_or_404(Product, pk=pk)
    
    # Check permissions
    if not (request.user.is_super_admin or request.user.is_superuser):
        return HttpResponseForbidden("You don't have permission to edit products.")
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            
            # Handle image upload
            uploaded_image = form.cleaned_data.get('image')
            if uploaded_image:
                try:
                    product.image_url = upload_product_image(uploaded_image)
                except Exception as e:
                    messages.error(request, f'Image upload failed: {e}')
            
            product.save()
            messages.success(request, f'{product.name} has been updated successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/edit.html', {'form': form, 'product': product})


@login_required
def product_delete(request, pk):
    """Delete a product (super admins only)."""
    product = get_object_or_404(Product, pk=pk)
    
    # Check permissions
    if not (request.user.is_super_admin or request.user.is_superuser):
        return HttpResponseForbidden("You don't have permission to delete products.")
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'{product_name} has been deleted successfully!')
        return redirect('products_list')
    
    return render(request, 'products/delete.html', {'product': product})
