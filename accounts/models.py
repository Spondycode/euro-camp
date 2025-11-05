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
