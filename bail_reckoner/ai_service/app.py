from flask import Flask, request, jsonify
import os
import sys
import json
import base64
from dotenv import load_dotenv
import vertexai
from vertexai.preview import caching
from vertexai.preview.generative_models import GenerativeModel
from vertexai.generative_models import Part, SafetySetting

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Vertex AI
vertexai.init(
    project=os.getenv("VERTEX_AI_PROJECT"),
    location=os.getenv("VERTEX_AI_LOCATION")
)

# Global variables for cached content
cached_content_name = None

# Configuration for the model
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0,
    "top_p": 0.95,
}

# Safety settings
safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
]

from flask import Flask, request, jsonify
import os
import sys
import json
import base64
from dotenv import load_dotenv
import vertexai
from vertexai.preview import caching
from vertexai.preview.generative_models import GenerativeModel
from vertexai.generative_models import Part, SafetySetting

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Vertex AI
vertexai.init(
    project=os.getenv("VERTEX_AI_PROJECT"),
    location=os.getenv("VERTEX_AI_LOCATION")
)

# Global variables for cached content
cached_content_name = None

# Configuration for the model
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0,
    "top_p": 0.95,
}

# Safety settings
safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

@app.route('/initialize', methods=['POST'])
def initialize_cache():
    """Initialize the AI model with legal documents"""
    global cached_content_name
    
    try:
        # System instructions for legal expertise
        system_instruction = """You are an expert legal assistant well-versed in Indian criminal law, specializing in the Bharatiya Nyaya Sanhita (BNS), Bharatiya Nagarik Suraksha Sanhita (BNSS), and Bharatiya Sakshya Adhiniyam (Indian Evidence Act) 2023. Your role is to assist judges, lawyers, and police officers by providing precise legal information and interpretations based on these laws, offering case-specific guidance for bail applications.

When providing legal analysis or answering queries, do the following:
1. Use relevant sections of the BNS, BNSS, and Bharatiya Sakshya Adhiniyam based on the specific scenario being queried.
2. Ensure the legal provisions, sections, and terminologies you use are from the 2023 versions of the law (not outdated versions).
3. Provide clear explanations of legal terms, procedures, and how they apply to the scenario.
4. Offer interpretations that reflect recent changes in the law to guide decision-making.
5. Focus specifically on bail eligibility criteria and assessment parameters."""
        
        # Get document paths from request
        data = request.json
        document_paths = data.get('document_paths', [])
        
        # Load documents
        documents = []
        for path in document_paths:
            with open(path, 'rb') as file:
                file_data = file.read()
                document = Part.from_data(
                    mime_type="application/pdf",
                    data=file_data
                )
                documents.append(document)
        
        # Create cached content
        import datetime
        cached_content = caching.CachedContent.create(
            model_name="gemini-1.5-pro-002",
            system_instruction=system_instruction,
            contents=documents,
            ttl=datetime.timedelta(hours=24),
            display_name="bail-reckoner-legal-cache",
        )
        
        cached_content_name = cached_content.name
        
        return jsonify({
            "status": "success",
            "message": "AI model initialized successfully",
            "cached_content_name": cached_content_name
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/assess_bail', methods=['POST'])
def assess_bail():
    """Assess bail eligibility based on case details"""
    global cached_content_name
    
    try:
        # Check if model is initialized
        if not cached_content_name:
            return jsonify({
                "status": "error",
                "message": "AI model not initialized. Call /initialize first."
            }), 400
        
        # Get case details from request
        data = request.json
        case_details = data.get('case_details', '')
        documents = data.get('documents', [])
        
        # Prepare case text
        case_text = f"""Analyze the following case for bail eligibility under India's new criminal laws:

{case_details}

Questions for Legal Assessment:
1. Under the Bharatiya Nyaya Sanhita (BNS), what are the charges applicable in this case and their bail provisions?
2. Based on the Bharatiya Nagarik Suraksha Sanhita (BNSS), is this case eligible for bail? Why or why not?
3. How should the court treat the evidence in this case under the Bharatiya Sakshya Adhiniyam?
4. Provide a bail eligibility score from 0-100 and justify your assessment.
5. What conditions should be imposed if bail is granted?"""
        
        # Prepare document parts
        document_parts = []
        for doc in documents:
            if doc.get('content') and doc.get('mime_type'):
                document_part = Part.from_data(
                    mime_type=doc['mime_type'],
                    data=base64.b64decode(doc['content'])
                )
                document_parts.append(document_part)
        
        # Get cached content
        cached_content = caching.CachedContent(cached_content_name=cached_content_name)
        model = GenerativeModel.from_cached_content(cached_content=cached_content)
        
        # Generate content
        content_parts = [case_text] + document_parts
        
        responses = model.generate_content(
            content_parts,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,
        )
        
        assessment_text = responses.candidates[0].content.parts[0].text
        
        # Extract bail eligibility score (assuming the model includes it in the response)
        import re
        score_match = re.search(r'bail eligibility score.*?(\d+)', assessment_text, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else None
        
        # Process the assessment text to create structured response
        assessment_result = {
            "full_assessment": assessment_text,
            "bail_eligibility_score": score,
            "charges_analysis": assessment_text,
            "bail_eligibility": assessment_text,
            "evidence_analysis": assessment_text,
            "recommended_conditions": assessment_text
        }
        
        return jsonify({
            "status": "success",
            "assessment": assessment_result,
            "usage_metadata": responses.usage_metadata._asdict() if hasattr(responses, 'usage_metadata') else {}
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))    