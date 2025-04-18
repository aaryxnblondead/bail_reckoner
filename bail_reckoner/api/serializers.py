from rest_framework import serializers
from assessment.models import Case, BailApplication, Document
from authentication.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type']
        read_only_fields = ['user_type']

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['document_id', 'uploaded_by', 'uploaded_at', 'blockchain_hash']
    
    def get_uploaded_by_name(self, obj):
        return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}"
    
    def create(self, validated_data):
        # Set the uploaded_by field to the current user
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)

class CaseSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    applicant_name = serializers.SerializerMethodField()
    legal_representative_name = serializers.SerializerMethodField()
    judicial_authority_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Case
        fields = '__all__'
        read_only_fields = ['case_id', 'created_at', 'updated_at']
    
    def get_applicant_name(self, obj):
        if obj.applicant:
            return f"{obj.applicant.first_name} {obj.applicant.last_name}"
        return None
    
    def get_legal_representative_name(self, obj):
        if obj.legal_representative:
            return f"{obj.legal_representative.first_name} {obj.legal_representative.last_name}"
        return None
    
    def get_judicial_authority_name(self, obj):
        if obj.judicial_authority:
            return f"{obj.judicial_authority.first_name} {obj.judicial_authority.last_name}"
        return None

class BailApplicationSerializer(serializers.ModelSerializer):
    case_details = serializers.SerializerMethodField()
    
    class Meta:
        model = BailApplication
        fields = '__all__'
        read_only_fields = ['application_id', 'ai_assessment_score', 'ai_assessment_report', 
                           'submitted_at', 'reviewed_at', 'blockchain_hash']
    
    def get_case_details(self, obj):
        return {
            'case_id': obj.case.case_id,
            'court_case_number': obj.case.court_case_number,
            'fir_number': obj.case.fir_number,
            'applicant_name': f"{obj.case.applicant.first_name} {obj.case.applicant.last_name}" if obj.case.applicant else None
        }