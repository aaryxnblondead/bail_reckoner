from django.db import models
from authentication.models import User
import uuid

class Case(models.Model):
    CASE_STATUS = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    case_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fir_number = models.CharField(max_length=50)
    court_case_number = models.CharField(max_length=50)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases')
    legal_representative = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='represented_cases')
    judicial_authority = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cases')
    charges = models.TextField()
    status = models.CharField(max_length=20, choices=CASE_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Case {self.court_case_number}"

class BailApplication(models.Model):
    APPLICATION_STATUS = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('ai_assessed', 'AI Assessed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    application_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='bail_applications')
    applicant_statement = models.TextField()
    grounds_for_bail = models.TextField()
    previous_bail_attempts = models.IntegerField(default=0)
    ai_assessment_score = models.FloatField(null=True, blank=True)
    ai_assessment_report = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    blockchain_hash = models.CharField(max_length=64, null=True, blank=True)
    
    def __str__(self):
        return f"Bail Application for {self.case}"

class Document(models.Model):
    DOCUMENT_TYPES = (
        ('fir', 'FIR'),
        ('charge_sheet', 'Charge Sheet'),
        ('court_order', 'Court Order'),
        ('medical_report', 'Medical Report'),
        ('witness_statement', 'Witness Statement'),
        ('other', 'Other'),
    )
    
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='case_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    blockchain_hash = models.CharField(max_length=64, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_document_type_display()}: {self.title}"