from django.db import models
from django.conf import settings


class Campsite(models.Model):
    """Model representing a campsite."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    map_location = models.CharField(max_length=500, help_text="GPS coordinates or map URL")
    website = models.URLField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='campsites')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Campsite'
        verbose_name_plural = 'Campsites'

    def __str__(self):
        return f"{self.name} - {self.country}"
