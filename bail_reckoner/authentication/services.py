import requests
import os
from django.conf import settings

class AadhaarVerificationService:
    """Service for Aadhaar verification"""
    
    def __init__(self):
        self.api_url = settings.AADHAAR_API_URL
        self.api_key = settings.AADHAAR_API_KEY
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def generate_otp(self, aadhaar_number):
        """Generate OTP for Aadhaar verification"""
        try:
            payload = {
                'aadhaar_number': aadhaar_number
            }
            
            response = requests.post(
                f"{self.api_url}/generate-otp",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'OTP sent successfully'
                }
            else:
                return {
                    'success': False,
                    'message': response.json().get('message', 'Failed to generate OTP')
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def verify_aadhaar(self, aadhaar_number, otp):
        """Verify Aadhaar using OTP"""
        try:
            payload = {
                'aadhaar_number': aadhaar_number,
                'otp': otp
            }
            
            response = requests.post(
                f"{self.api_url}/verify-otp",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Aadhaar verification successful',
                    'data': response.json().get('data', {})
                }
            else:
                return {
                    'success': False,
                    'message': response.json().get('message', 'Aadhaar verification failed')
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }