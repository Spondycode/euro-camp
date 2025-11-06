from django.contrib import admin
from .models import Campsite


def approve_campsites(modeladmin, request, queryset):
    """Admin action to approve selected campsites."""
    updated = queryset.update(is_approved=True)
    modeladmin.message_user(request, f'{updated} campsite(s) approved.')
approve_campsites.short_description = "Approve selected campsites"


def reject_campsites(modeladmin, request, queryset):
    """Admin action to reject (delete) selected campsites."""
    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(request, f'{count} campsite(s) rejected and deleted.')
reject_campsites.short_description = "Reject and delete selected campsites"


@admin.register(Campsite)
class CampsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'is_approved', 'is_premium', 'suggested_by', 'created_by', 'created_at')
    list_filter = ('is_approved', 'is_premium', 'country', 'created_at')
    search_fields = ('name', 'country', 'description', 'suggested_by__username')
    ordering = ('name',)
    actions = [approve_campsites, reject_campsites]
    list_editable = ('is_premium',)
    
    readonly_fields = ('created_at', 'updated_at')
