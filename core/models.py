from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class Campsite(models.Model):
    """Model representing a campsite."""
    
    # European countries choices
    COUNTRY_CHOICES = [
        ('AL', 'Albania'),
        ('AD', 'Andorra'),
        ('AT', 'Austria'),
        ('BY', 'Belarus'),
        ('BE', 'Belgium'),
        ('BA', 'Bosnia and Herzegovina'),
        ('BG', 'Bulgaria'),
        ('HR', 'Croatia'),
        ('CY', 'Cyprus'),
        ('CZ', 'Czech Republic'),
        ('DK', 'Denmark'),
        ('EE', 'Estonia'),
        ('FI', 'Finland'),
        ('FR', 'France'),
        ('DE', 'Germany'),
        ('GR', 'Greece'),
        ('HU', 'Hungary'),
        ('IS', 'Iceland'),
        ('IE', 'Ireland'),
        ('IT', 'Italy'),
        ('XK', 'Kosovo'),
        ('LV', 'Latvia'),
        ('LI', 'Liechtenstein'),
        ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
        ('MT', 'Malta'),
        ('MD', 'Moldova'),
        ('MC', 'Monaco'),
        ('ME', 'Montenegro'),
        ('NL', 'Netherlands'),
        ('MK', 'North Macedonia'),
        ('NO', 'Norway'),
        ('PL', 'Poland'),
        ('PT', 'Portugal'),
        ('RO', 'Romania'),
        ('RU', 'Russia'),
        ('SM', 'San Marino'),
        ('RS', 'Serbia'),
        ('SK', 'Slovakia'),
        ('SI', 'Slovenia'),
        ('ES', 'Spain'),
        ('SE', 'Sweden'),
        ('CH', 'Switzerland'),
        ('UA', 'Ukraine'),
        ('GB', 'United Kingdom'),
        ('VA', 'Vatican City'),
    ]
    
    name = models.CharField(max_length=255)
    town = models.CharField(max_length=200)
    description = models.TextField()
    map_location = models.CharField(max_length=500, help_text="GPS coordinates or map URL")
    website = models.URLField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Primary image hosted on ImageKit")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='campsites')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Approval and suggestion tracking
    is_approved = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this campsite has been approved for display"
    )
    suggested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suggested_campsites',
        db_index=True,
        help_text="User who originally suggested this campsite"
    )
    is_premium = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Premium campsites are featured at the top of listings"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Campsite'
        verbose_name_plural = 'Campsites'

    def __str__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f"{self.name} - {self.get_country_display()} ({status})"
    
    @property
    def latitude(self):
        """Extract latitude from map_location field (expects 'lat,lng' format)."""
        if not self.map_location:
            return None
        try:
            parts = self.map_location.split(',')
            if len(parts) >= 2:
                lat = float(parts[0].strip())
                if -90 <= lat <= 90:
                    return lat
        except (ValueError, AttributeError):
            pass
        return None
    
    @property
    def longitude(self):
        """Extract longitude from map_location field (expects 'lat,lng' format)."""
        if not self.map_location:
            return None
        try:
            parts = self.map_location.split(',')
            if len(parts) >= 2:
                lng = float(parts[1].strip())
                if -180 <= lng <= 180:
                    return lng
        except (ValueError, AttributeError):
            pass
        return None


class CampsiteLike(models.Model):
    """Model representing a user's like of a campsite."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='campsite_likes'
    )
    campsite = models.ForeignKey(
        'Campsite',
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'campsite'],
                name='unique_campsite_like'
            ),
        ]
        ordering = ['-created_at']
        verbose_name = 'Campsite Like'
        verbose_name_plural = 'Campsite Likes'

    def __str__(self):
        return f"{self.user.username} likes {self.campsite.name}"


class Product(models.Model):
    """Model representing a camping product available for purchase."""
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Product image hosted externally (e.g., ImageKit)"
    )
    amazon_link = models.URLField(
        max_length=500,
        help_text="Amazon affiliate or product link"
    )
    is_featured = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Featured products are displayed on the products page"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name
