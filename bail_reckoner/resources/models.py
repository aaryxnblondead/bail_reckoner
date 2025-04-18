from django.db import models

class LegalResource(models.Model):
    RESOURCE_TYPES = (
        ('act', 'Act'),
        ('section', 'Section'),
        ('precedent', 'Precedent'),
        ('guideline', 'Guideline'),
        ('article', 'Article'),
    )
    
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    content = models.TextField()
    source = models.CharField(max_length=200)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"