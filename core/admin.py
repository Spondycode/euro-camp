from django.contrib import admin
from .models import Campsite


@admin.register(Campsite)
class CampsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'phone_number', 'website', 'created_at')
    list_filter = ('country', 'created_at')
    search_fields = ('name', 'country', 'description')
    ordering = ('name',)
