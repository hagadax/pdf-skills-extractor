"""
AI-based skill extraction module using OpenAI GPT models or Azure OpenAI.
This module provides intelligent skill extraction as an alternative to pattern matching.
Supports both OpenAI API and Azure OpenAI Service with secure Key Vault configuration.
"""

import os
import json
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
import time
import logging

# Import Key Vault manager
from keyvault_manager import get_application_config

# Support both OpenAI and Azure OpenAI
try:
    from openai import OpenAI, AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None
    AzureOpenAI = None
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class AISkillExtractor:
    """AI-powered skill extraction using OpenAI GPT models or Azure OpenAI."""
    
    def __init__(self):
        """Initialize the AI extractor with appropriate client using Key Vault configuration."""
        self.client = None
        self.model_name = "gpt-3.5-turbo"  # Default model
        
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI library not installed. AI extraction will be disabled.")
            return
        
        # Get configuration from Key Vault with environment fallbacks
        config = get_application_config()
        
        # Extract configuration values
        azure_endpoint = config.get('azure_openai_endpoint')
        azure_api_key = config.get('azure_openai_api_key')
        azure_deployment = config.get('azure_openai_deployment_name', 'gpt-35-turbo')
        openai_api_key = config.get('openai_api_key')
        
        # Initialize Azure OpenAI if configured
        if azure_endpoint and azure_api_key:
            try:
                self.client = AzureOpenAI(
                    azure_endpoint=azure_endpoint,
                    api_key=azure_api_key,
                    api_version="2024-02-15-preview"
                )
                self.model_name = azure_deployment
                self.service_type = "Azure OpenAI"
                logger.info(f"Initialized Azure OpenAI with deployment: {azure_deployment}")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {e}")
                self.client = None
                
        # Fall back to OpenAI if Azure not configured or failed
        elif openai_api_key and not self.client:
            try:
                self.client = OpenAI(api_key=openai_api_key)
                self.service_type = "OpenAI"
                logger.info("Initialized OpenAI client")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
        
        if not self.client:
            logger.warning("No AI service configured. Check Key Vault secrets or environment variables:")
            logger.warning("- Azure OpenAI: azure-openai-endpoint, azure-openai-api-key, azure-openai-deployment-name")
            logger.warning("- OpenAI: openai-api-key")

import os
import json
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
import time

# Support both OpenAI and Azure OpenAI
try:
    from openai import OpenAI, AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None
    AzureOpenAI = None
    OPENAI_AVAILABLE = False

class AISkillExtractor:
    """AI-powered skill extraction using OpenAI GPT models or Azure OpenAI."""
    
    def __init__(self):
        """Initialize the AI extractor with appropriate client."""
        self.client = None
        self.model_name = "gpt-3.5-turbo"  # Default model
        
        # Check for Azure OpenAI configuration first
        azure_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
        azure_api_key = os.environ.get('AZURE_OPENAI_API_KEY')
        azure_deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-35-turbo')
        
        # Check for regular OpenAI configuration
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        
        if not OPENAI_AVAILABLE:
            print("Warning: OpenAI library not installed. AI extraction will be disabled.")
            return
            
        # Initialize Azure OpenAI if configured
        if azure_endpoint and azure_api_key:
            try:
                self.client = AzureOpenAI(
                    azure_endpoint=azure_endpoint,
                    api_key=azure_api_key,
                    api_version="2024-02-15-preview"
                )
                self.model_name = azure_deployment
                self.service_type = "Azure OpenAI"
                print(f"Initialized Azure OpenAI with deployment: {azure_deployment}")
            except Exception as e:
                print(f"Failed to initialize Azure OpenAI: {e}")
                self.client = None
                
        # Fall back to OpenAI if Azure not configured or failed
        elif openai_api_key and not self.client:
            try:
                self.client = OpenAI(api_key=openai_api_key)
                self.service_type = "OpenAI"
                print("Initialized OpenAI client")
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}")
                self.client = None
        
        if not self.client:
            print("Warning: No AI service configured. Set either:")
            print("- Azure OpenAI: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME")
            print("- OpenAI: OPENAI_API_KEY")
        
        # AI model parameters
        self.max_tokens = 1000
        self.temperature = 0.1  # Low temperature for consistent results
        
        # AI-specific data structures
        self.ai_skill_counter = Counter()
        self.ai_skill_documents = defaultdict(list)
        self.ai_processed_documents = {}
        self.ai_monthly_skill_data = defaultdict(lambda: defaultdict(int))
        
        # Stats persistence for AI results
        self.ai_stats_blob_name = 'ai_stats.json'
        
    def extract_skills_from_text(self, text: str, filename: str) -> Tuple[List[str], Dict[str, Any]]:
        """
        Extract skills from text using OpenAI GPT model.
        
        Args:
            text: The text content to analyze
            filename: Name of the file being processed
            
        Returns:
            Tuple of (skills_list, analysis_metadata)
        """
        if not self.client:
            print("Warning: No AI client configured. Skipping AI extraction.")
            return [], {}
        
        try:
            # Prepare the prompt for skill extraction
            prompt = self._create_skill_extraction_prompt(text, filename)
            
            # Call AI API (works for both OpenAI and Azure OpenAI)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical recruiter and skill analyst. Extract technology skills from documents with high accuracy."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9
            )
            
            # Parse the response
            result = response.choices[0].message.content
            skills_data = self._parse_ai_response(result)
            
            # Extract metadata
            metadata = {
                'model_used': self.model_name,
                'service_type': self.service_type,
                'tokens_used': response.usage.total_tokens if response.usage else 0,
                'processing_time': datetime.now().isoformat(),
                'confidence_scores': skills_data.get('confidence_scores', {}),
                'skill_categories': skills_data.get('categories', {}),
                'analysis_notes': skills_data.get('notes', '')
            }
            
            return skills_data.get('skills', []), metadata
            
        except Exception as e:
            print(f"Error in AI skill extraction: {e}")
            return [], {'error': str(e)}
    
    def _create_skill_extraction_prompt(self, text: str, filename: str) -> str:
        """Create a detailed prompt for skill extraction."""
        
        # Truncate text if too long to fit in context window
        max_text_length = 8000  # Leave room for prompt and response
        if len(text) > max_text_length:
            text = text[:max_text_length] + "..."
        
        prompt = f"""
Analyze this document and extract ALL technology skills mentioned. Be comprehensive and accurate.

Document Name: {filename}
Document Content:
{text}

Please extract skills in the following categories and return as JSON:

1. Programming Languages (Python, Java, JavaScript, C++, etc.)
2. Web Technologies (React, Angular, Vue.js, HTML, CSS, etc.)
3. Databases (MySQL, MongoDB, PostgreSQL, Redis, etc.)
4. Cloud Platforms (AWS, Azure, Google Cloud, etc.)
5. DevOps & Tools (Docker, Kubernetes, Jenkins, Git, etc.)
6. Mobile Development (iOS, Android, React Native, Flutter, etc.)
7. Data Science & AI (Machine Learning, TensorFlow, PyTorch, etc.)
8. Testing Frameworks (Jest, Pytest, Selenium, etc.)
9. Operating Systems & Infrastructure
10. Other Technical Skills

For each skill found, provide:
- Skill name (standardized)
- Confidence score (0.0-1.0)
- Context where it was mentioned
- Category

Return the response in this JSON format:
{{
    "skills": ["skill1", "skill2", ...],
    "detailed_analysis": [
        {{
            "skill": "skill_name",
            "confidence": 0.95,
            "category": "Programming Languages",
            "context": "brief context where mentioned",
            "variations_found": ["React", "React.js", "ReactJS"]
        }}
    ],
    "confidence_scores": {{"skill1": 0.95, "skill2": 0.87}},
    "categories": {{"Programming Languages": ["Python", "Java"], "Databases": ["MySQL"]}},
    "notes": "Brief analysis notes about the document and skill extraction quality"
}}

Focus on:
- Technical skills only (no soft skills)
- Standardized naming (e.g., "JavaScript" not "JS")
- High confidence extraction
- Avoid duplicates
- Include skill variations and aliases
"""
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response and extract structured data."""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                # Fallback: extract skills from text format
                return self._extract_skills_from_text_response(response_text)
            
            json_str = response_text[start_idx:end_idx + 1]
            data = json.loads(json_str)
            
            # Validate and clean the data
            skills = data.get('skills', [])
            skills = [skill.strip() for skill in skills if skill.strip()]
            
            return {
                'skills': skills,
                'detailed_analysis': data.get('detailed_analysis', []),
                'confidence_scores': data.get('confidence_scores', {}),
                'categories': data.get('categories', {}),
                'notes': data.get('notes', '')
            }
            
        except json.JSONDecodeError:
            # Fallback parsing for non-JSON responses
            return self._extract_skills_from_text_response(response_text)
    
    def _extract_skills_from_text_response(self, response_text: str) -> Dict[str, Any]:
        """Fallback method to extract skills from plain text response."""
        skills = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for bullet points or numbered lists
            if line.startswith(('- ', '* ', '• ')) or (len(line) > 2 and line[0].isdigit() and line[1] == '.'):
                # Extract skill name from the line
                skill = line[2:].strip() if line.startswith(('- ', '* ', '• ')) else line[3:].strip()
                # Clean up the skill name
                skill = skill.split('(')[0].strip()  # Remove parenthetical explanations
                skill = skill.split(':')[0].strip()  # Remove colons and descriptions
                if skill and len(skill) < 50:  # Reasonable skill name length
                    skills.append(skill)
        
        return {
            'skills': skills,
            'detailed_analysis': [],
            'confidence_scores': {},
            'categories': {},
            'notes': 'Fallback text parsing used due to JSON parsing error'
        }
    
    def update_ai_stats(self, skills: List[str], filename: str, upload_date: str, 
                       file_date: str, file_type: str, metadata: Dict[str, Any]):
        """Update AI-specific statistics."""
        
        # Get month key for tracking
        date_for_tracking = file_date if file_date else upload_date.split(' ')[0]
        month_key = date_for_tracking[:7]  # Get YYYY-MM format
        
        # Update AI skill counter
        for skill in skills:
            self.ai_skill_counter[skill] += 1
            
            # Track monthly data
            self.ai_monthly_skill_data[skill][month_key] += 1
            
            # Track which document contains this skill
            self.ai_skill_documents[skill].append({
                'filename': filename,
                'upload_date': upload_date,
                'file_date': file_date or upload_date.split(' ')[0],
                'file_type': file_type,
                'confidence': metadata.get('confidence_scores', {}).get(skill, 1.0)
            })
        
        # Track processed document
        self.ai_processed_documents[filename] = {
            'upload_date': upload_date,
            'file_date': file_date or upload_date.split(' ')[0],
            'skills_found': skills,
            'file_type': file_type,
            'ai_metadata': metadata,
            'extraction_method': 'AI (OpenAI GPT)'
        }
    
    def get_ai_stats_data(self) -> Dict[str, Any]:
        """Get AI extraction statistics for saving."""
        return {
            'ai_skill_counter': dict(self.ai_skill_counter),
            'ai_skill_documents': dict(self.ai_skill_documents),
            'ai_processed_documents': self.ai_processed_documents,
            'ai_monthly_skill_data': {
                skill: dict(months) for skill, months in self.ai_monthly_skill_data.items()
            },
            'last_updated': datetime.now().isoformat(),
            'version': '1.0',
            'extraction_method': 'AI (OpenAI GPT)'
        }
    
    def load_ai_stats_data(self, stats_data: Dict[str, Any]):
        """Load AI extraction statistics."""
        self.ai_skill_counter = Counter(stats_data.get('ai_skill_counter', {}))
        
        # Restore ai_skill_documents
        skill_docs_data = stats_data.get('ai_skill_documents', {})
        self.ai_skill_documents = defaultdict(list)
        for skill, docs in skill_docs_data.items():
            self.ai_skill_documents[skill] = docs
        
        self.ai_processed_documents = stats_data.get('ai_processed_documents', {})
        
        # Restore monthly data
        monthly_data = stats_data.get('ai_monthly_skill_data', {})
        self.ai_monthly_skill_data = defaultdict(lambda: defaultdict(int))
        for skill, months in monthly_data.items():
            self.ai_monthly_skill_data[skill] = defaultdict(int, months)
    
    def get_ai_monthly_chart_data(self):
        """Generate chart data for AI-extracted skills."""
        from datetime import datetime, timedelta
        
        current_date = datetime.now()
        months = []
        
        # Generate list of last 12 months
        for i in range(11, -1, -1):
            date = current_date - timedelta(days=i*30)
            month_key = date.strftime('%Y-%m')
            month_label = date.strftime('%b %Y')
            months.append({'key': month_key, 'label': month_label})
        
        # Get top 10 AI-extracted skills
        top_skills = [skill for skill, count in self.ai_skill_counter.most_common(10)]
        
        # Prepare chart data
        chart_data = {
            'labels': [month['label'] for month in months],
            'datasets': []
        }
        
        # Color palette (different from main chart)
        colors = [
            '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b',
            '#eb4d4b', '#6c5ce7', '#fd79a8', '#fdcb6e', '#00b894'
        ]
        
        # Create dataset for each top skill
        for i, skill in enumerate(top_skills):
            skill_data = []
            cumulative_count = 0
            
            for month in months:
                monthly_occurrences = self.ai_monthly_skill_data[skill].get(month['key'], 0)
                cumulative_count += monthly_occurrences
                skill_data.append(cumulative_count)
            
            if cumulative_count > 0:
                chart_data['datasets'].append({
                    'label': f"AI: {skill}",
                    'data': skill_data,
                    'borderColor': colors[i % len(colors)],
                    'backgroundColor': colors[i % len(colors)] + '20',
                    'tension': 0.4,
                    'fill': False,
                    'borderDash': [5, 5]  # Dashed line to distinguish from pattern matching
                })
        
        return chart_data

# Global AI extractor instance
ai_extractor = AISkillExtractor()