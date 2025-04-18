import os
import json
import requests
import hashlib
from django.conf import settings

class BlockchainService:
    """Service for interacting with Hyperledger Fabric blockchain"""
    
    def __init__(self):
        self.api_url = settings.HYPERLEDGER_API_URL
        self.api_key = settings.HYPERLEDGER_API_KEY
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def create_document_hash(self, document_content, metadata):
        """Create a hash of document content and metadata"""
        # Combine document content and metadata
        if isinstance(document_content, bytes):
            content_hash = hashlib.sha256(document_content).hexdigest()
        else:
            content_hash = hashlib.sha256(document_content.encode('utf-8')).hexdigest()
        
        metadata_str = json.dumps(metadata, sort_keys=True)
        combined = content_hash + metadata_str
        
        # Create final hash
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    def store_document_hash(self, document_hash, metadata):
        """Store document hash on blockchain"""
        try:
            payload = {
                'docHash': document_hash,
                'metadata': metadata
            }
            
            response = requests.post(
                f"{self.api_url}/documents",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                raise Exception(f"Failed to store document hash: {response.text}")
        
        except Exception as e:
            # Log the error
            print(f"Blockchain error: {str(e)}")
            raise
    
    def verify_document_hash(self, document_hash):
        """Verify if document hash exists on blockchain"""
        try:
            response = requests.get(
                f"{self.api_url}/documents/{document_hash}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                raise Exception(f"Failed to verify document hash: {response.text}")
        
        except Exception as e:
            # Log the error
            print(f"Blockchain error: {str(e)}")
            raise
    
    def store_bail_application(self, application_id, application_data):
        """Store bail application data on blockchain"""
        try:
            # Create hash of application data
            application_str = json.dumps(application_data, sort_keys=True)
            application_hash = hashlib.sha256(application_str.encode('utf-8')).hexdigest()
            
            payload = {
                'applicationId': str(application_id),
                'applicationHash': application_hash,
                'metadata': {
                    'type': 'bail_application',
                    'timestamp': application_data.get('submitted_at', ''),
                    'status': application_data.get('status', '')
                }
            }
            
            response = requests.post(
                f"{self.api_url}/applications",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200 or response.status_code == 201:
                return application_hash
            else:
                raise Exception(f"Failed to store bail application: {response.text}")
        
        except Exception as e:
            # Log the error
            print(f"Blockchain error: {str(e)}")
            raise