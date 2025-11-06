from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        PAGE_ADMIN = "page_admin", "Page Admin"
        USER = "user", "User"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser
    
    @property
    def approved_campsites_count(self):
        """Count of approved campsites suggested by this user."""
        from django.apps import apps
        Campsite = apps.get_model("core", "Campsite")
        return Campsite.objects.filter(suggested_by=self, is_approved=True).count()
    
    @property
    def can_auto_approve_campsites(self):
        """Returns True if user has 3 or more approved campsite suggestions."""
        return self.approved_campsites_count >= 3
