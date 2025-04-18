from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPES = (
        ('prisoner', 'Undertrial Prisoner'),
        ('lawyer', 'Legal Representative'),
        ('judge', 'Judicial Authority'),
        ('admin', 'System Administrator'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    aadhaar_id = models.CharField(max_length=12, blank=True, null=True)
    bar_council_id = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"