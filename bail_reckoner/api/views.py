from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import requests
import json
import base64
import os
from assessment.models import Case, BailApplication, Document
from .serializers import CaseSerializer, BailApplicationSerializer, DocumentSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initialize_ai_service(request):
    """Initialize the AI service with legal documents"""
    try:
        # Get paths to legal documents
        document_paths = [
            os.path.join(settings.MEDIA_ROOT, 'legal_docs/bns.pdf'),
            os.path.join(settings.MEDIA_ROOT, 'legal_docs/bnss.pdf'),
            os.path.join(settings.MEDIA_ROOT, 'legal_docs/bsa.pdf')
        ]
        
        # Call the AI service
        response = requests.post(
            f"{settings.AI_SERVICE_URL}/initialize",
            json={"document_paths": document_paths},
            timeout=300  # 5-minute timeout for initialization
        )
        
        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to initialize AI service", "details": response.json()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assess_bail_application(request, application_id):
    """Send a bail application for AI assessment"""
    try:
        # Get the bail application
        bail_application = BailApplication.objects.get(application_id=application_id)
        
        # Check if user has permission to assess this application
        if not request.user.is_staff and request.user != bail_application.case.applicant and request.user != bail_application.case.legal_representative:
            return Response(
                {"error": "You don't have permission to assess this application"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Prepare case details
        case = bail_application.case
        case_details = f"""
Case Number: {case.court_case_number}
FIR Number: {case.fir_number}
Charges: {case.charges}

Applicant Statement: {bail_application.applicant_statement}
Grounds for Bail: {bail_application.grounds_for_bail}
Previous Bail Attempts: {bail_application.previous_bail_attempts}
        """
        
        # Get documents related to the case
        documents = []
        for doc in Document.objects.filter(case=case):
            with open(doc.file.path, 'rb') as file:
                encoded_content = base64.b64encode(file.read()).decode('utf-8')
                documents.append({
                    "content": encoded_content,
                    "mime_type": get_mime_type(doc.file.name),
                    "document_type": doc.document_type
                })
        
        # Call the AI service
        response = requests.post(
            f"{settings.AI_SERVICE_URL}/assess_bail",
            json={
                "case_details": case_details,
                "documents": documents
            },
            timeout=300  # 5-minute timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Update the bail application with AI assessment
            bail_application.ai_assessment_score = result['assessment'].get('bail_eligibility_score')
            bail_application.ai_assessment_report = result['assessment']
            bail_application.status = 'ai_assessed'
            bail_application.save()
            
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to assess bail application", "details": response.json()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except BailApplication.DoesNotExist:
        return Response(
            {"error": "Bail application not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_document(request):
    """Analyze a specific document using the AI service"""
    try:
        # Get document details from request
        document_id = request.data.get('document_id')
        query = request.data.get('query', 'Summarize this document and extract key legal points relevant to bail.')
        
        # Get the document
        document = Document.objects.get(document_id=document_id)
        
        # Check if user has permission to analyze this document
        case = document.case
        if not request.user.is_staff and request.user != case.applicant and request.user != case.legal_representative and request.user != case.judicial_authority:
            return Response(
                {"error": "You don't have permission to analyze this document"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Read and encode the document
        with open(document.file.path, 'rb') as file:
            encoded_content = base64.b64encode(file.read()).decode('utf-8')
        
        # Call the AI service
        response = requests.post(
            f"{settings.AI_SERVICE_URL}/analyze_document",
            json={
                "document_content": encoded_content,
                "document_type": document.get_document_type_display(),
                "mime_type": get_mime_type(document.file.name),
                "query": query
            },
            timeout=180  # 3-minute timeout
        )
        
        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to analyze document", "details": response.json()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Document.DoesNotExist:
        return Response(
            {"error": "Document not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def get_mime_type(filename):
    """Get MIME type based on file extension"""
    extension = filename.split('.')[-1].lower()
    mime_types = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'txt': 'text/plain',
        'mp4': 'video/mp4'
    }
    return mime_types.get(extension, 'application/octet-stream')

# ViewSets for RESTful API
class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter cases based on user role"""
        user = self.request.user
        
        if user.is_staff or user.user_type == 'judge':
            return Case.objects.all()
        elif user.user_type == 'lawyer':
            return Case.objects.filter(legal_representative=user)
        else:  # prisoner
            return Case.objects.filter(applicant=user)

class BailApplicationViewSet(viewsets.ModelViewSet):
    queryset = BailApplication.objects.all()
    serializer_class = BailApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter bail applications based on user role"""
        user = self.request.user
        
        if user.is_staff or user.user_type == 'judge':
            return BailApplication.objects.all()
        elif user.user_type == 'lawyer':
            return BailApplication.objects.filter(case__legal_representative=user)
        else:  # prisoner
            return BailApplication.objects.filter(case__applicant=user)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter documents based on user role"""
        user = self.request.user
        
        if user.is_staff or user.user_type == 'judge':
            return Document.objects.all()
        elif user.user_type == 'lawyer':
            return Document.objects.filter(case__legal_representative=user)
        else:  # prisoner
            return Document.objects.filter(case__applicant=user)