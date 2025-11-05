from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Campsite


def home(request):
    """Render the home page."""
    return render(request, 'home.html')


@login_required
def campsites_list(request):
    """Display list of all campsites."""
    campsites = Campsite.objects.all()
    return render(request, 'campsites/list.html', {'campsites': campsites})


@login_required
def campsite_detail(request, pk):
    """Display details of a specific campsite."""
    from django.shortcuts import get_object_or_404
    campsite = get_object_or_404(Campsite, pk=pk)
    return render(request, 'campsites/detail.html', {'campsite': campsite})
