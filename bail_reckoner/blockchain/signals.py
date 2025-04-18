from django.db.models.signals import post_save
from django.dispatch import receiver
from assessment.models import Document, BailApplication
from .services import BlockchainService

@receiver(post_save, sender=Document)
def document_post_save(sender, instance, created, **kwargs):
    """Store document hash on blockchain when a new document is created"""
    if created and not instance.blockchain_hash:
        try:
            # Initialize blockchain service
            blockchain_service = BlockchainService()
            
            # Read document content
            with open(instance.file.path, 'rb') as file:
                document_content = file.read()
            
            # Create metadata
            metadata = {
                'document_id': str(instance.document_id),
                'document_type': instance.document_type,
                'title': instance.title,
                'case_id': str(instance.case.case_id),
                'uploaded_by': instance.uploaded_by.username,
                'uploaded_at': instance.uploaded_at.isoformat()
            }
            
            # Create document hash
            document_hash = blockchain_service.create_document_hash(document_content, metadata)
            
            # Store hash on blockchain
            blockchain_service.store_document_hash(document_hash, metadata)
            
            # Update document with blockchain hash
            instance.blockchain_hash = document_hash
            instance.save(update_fields=['blockchain_hash'])
        
        except Exception as e:
            # Log the error but don't prevent document creation
            print(f"Failed to store document on blockchain: {str(e)}")

@receiver(post_save, sender=BailApplication)
def bail_application_post_save(sender, instance, **kwargs):
    """Store bail application on blockchain when status changes to submitted or approved/rejected"""
    if instance.status in ['submitted', 'approved', 'rejected'] and not instance.blockchain_hash:
        try:
            # Initialize blockchain service
            blockchain_service = BlockchainService()
            
            # Create application data
            application_data = {
                'application_id': str(instance.application_id),
                'case_id': str(instance.case.case_id),
                'applicant_statement': instance.applicant_statement,
                'grounds_for_bail': instance.grounds_for_bail,
                'previous_bail_attempts': instance.previous_bail_attempts,
                'status': instance.status,
                'submitted_at': instance.submitted_at.isoformat() if instance.submitted_at else None,
                'reviewed_at': instance.reviewed_at.isoformat() if instance.reviewed_at else None,
                'ai_assessment_score': instance.ai_assessment_score
            }
            
            # Store application on blockchain
            application_hash = blockchain_service.store_bail_application(
                instance.application_id, 
                application_data
            )
            
            # Update application with blockchain hash
            instance.blockchain_hash = application_hash
            instance.save(update_fields=['blockchain_hash'])
        
        except Exception as e:
            # Log the error but don't prevent application update
            print(f"Failed to store bail application on blockchain: {str(e)}")