"""
AI-based skill extraction module using OpenAI GPT models or Azure OpenAI.
This module provides intelligent skill extraction as an alternative to pattern matching.
Supports both OpenAI API and Azure OpenAI Service with secure Key Vault configuration.
"""

import os
import json
from datetime import datetime, timedelta
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
        self.service_type = "None"
        
        # Initialize skill tracking
        self.ai_skill_counter = Counter()
        self.ai_monthly_skill_data = defaultdict(lambda: defaultdict(int))
        self.ai_processed_documents = {}
        self.ai_skill_documents = defaultdict(list)
        self.ai_stats_blob_name = "ai_skills_stats.json"
        
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI library not installed. AI extraction will be disabled.")
            return
        
        # Get configuration from Key Vault
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
            logger.warning("No AI service configured. Check Key Vault secrets:")
            logger.warning("- Azure OpenAI: azure-openai-endpoint, azure-openai-api-key, azure-openai-deployment-name")
            logger.warning("- OpenAI: openai-api-key")

    def extract_skills_from_text(self, text: str, document_type: str = "unknown") -> Tuple[List[str], Dict[str, Any]]:
        """
        Extract skills from text using AI.
        
        Args:
            text: Text to extract skills from
            document_type: Type of document (resume, job_description, etc.)
            
        Returns:
            Tuple of (skill_list, metadata_dict)
        """
        if not self.client:
            logger.warning("No AI client configured. Skipping AI extraction.")
            return [], {}
            
        try:
            prompt = self._create_skill_extraction_prompt(text, document_type)
            
            # Make API call with retry logic
            response = self._make_api_call_with_retry(prompt)
            
            if response:
                skills = self._parse_ai_response(response)
                
                # Track skills for analytics
                self._track_extracted_skills(skills)
                
                metadata = {
                    "extraction_method": "ai",
                    "ai_service": self.service_type,
                    "model": self.model_name,
                    "timestamp": datetime.now().isoformat(),
                    "document_type": document_type,
                    "skill_count": len(skills)
                }
                
                return skills, metadata
            else:
                return [], {}
                
        except Exception as e:
            logger.error(f"Error during AI skill extraction: {e}")
            return [], {}
    
    def _create_skill_extraction_prompt(self, text: str, document_type: str) -> str:
        """Create a well-structured prompt for skill extraction with multilingual support."""
        
        prompt_templates = {
            "resume": """
Analyze this resume/CV and extract ALL technical and professional skills mentioned. 
The text may be in Norwegian, English, or a combination of both languages.
Include programming languages, frameworks, tools, methodologies, certifications, and soft skills.

Important: This text may contain PDF extraction artifacts and corrupted characters - focus on extracting meaningful skills despite text corruption.

Resume/CV text:
{text}

Return a JSON array of skills in this format:
["Python", "React", "Docker", "Agile", "Communication", ...]

Rules:
- Handle both Norwegian and English text seamlessly
- Include both technical and soft skills
- Standardize skill names in English (e.g., "JavaScript" not "JS", "Kommunikasjon" -> "Communication")
- Ignore PDF extraction artifacts and corrupted text
- Don't include company names, job titles, or locations
- Focus on transferable skills and competencies
- Interpret Norwegian skill terms and translate to English equivalents:
  * "samarbeid" -> "Team Collaboration"  
  * "problemløsning" -> "Problem Solving"
  * "lederskap" -> "Leadership"
  * "kommunikasjon" -> "Communication"
  * "utvikler/developer" -> Backend/Frontend Development (contextually)
""",
            "job_description": """
Analyze this job description and extract ALL required and preferred skills.
The text may be in Norwegian, English, or a combination of both languages.
Include technical skills, tools, frameworks, methodologies, and soft skills.

Important: This text may contain PDF extraction artifacts and corrupted characters - focus on extracting meaningful skills despite text corruption.

Job description:
{text}

Return a JSON array of skills in this format:
["Java", "Spring Boot", "Kubernetes", "Leadership", "Problem Solving", ...]

Rules:
- Handle both Norwegian and English text seamlessly
- Include both technical and soft skills (both required and preferred)
- Standardize skill names in English
- Ignore PDF extraction artifacts and corrupted text
- Don't include company-specific terms, locations, or salary information
- Interpret Norwegian requirement terms and translate to English equivalents:
  * "erfaring med" -> experience requirement (extract the technology)
  * "kjennskap til" -> knowledge requirement (extract the technology)
  * "gode ferdigheter i" -> proficiency requirement (extract the skill)
  * Common Norwegian tech terms: "utvikling" (development), "rammeverk" (framework), etc.
""",
            "default": """
Analyze this text and extract professional skills, technologies, and competencies mentioned.
The text may be in Norwegian, English, or mixed languages, and may contain PDF extraction artifacts.

Text:
{text}

Return a JSON array of skills in this format:
["Skill1", "Skill2", "Skill3", ...]

Rules:
- Handle multilingual content (Norwegian/English)
- Focus on technical and professional skills
- Standardize skill names in English
- Ignore corrupted text and PDF artifacts
- Don't include irrelevant terms or locations
"""
        }
        
        template = prompt_templates.get(document_type, prompt_templates["default"])
        return template.format(text=text[:4000])  # Limit text length to avoid token limits
    
    def _make_api_call_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Make API call with retry logic."""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an expert at extracting professional skills from multilingual text (English/Norwegian). You can handle PDF extraction artifacts and corrupted text. Always return valid JSON arrays with standardized English skill names."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.1,  # Low temperature for consistent results
                    timeout=30
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                logger.warning(f"API call attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All API call attempts failed: {e}")
                    
        return None
    
    def _parse_ai_response(self, response: str) -> List[str]:
        """Parse AI response and extract skills list."""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Handle cases where response might have additional text
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                skills_raw = json.loads(json_str)
                
                # Clean and validate skills
                skills = []
                for skill in skills_raw:
                    if isinstance(skill, str) and len(skill.strip()) > 1:
                        # Clean up the skill name
                        clean_skill = skill.strip().title()
                        # Remove common prefixes/suffixes
                        clean_skill = clean_skill.replace('Programming', '').replace('Language', '').strip()
                        if clean_skill and clean_skill not in skills:
                            skills.append(clean_skill)
                
                return skills[:50]  # Limit to reasonable number
            else:
                logger.warning("No valid JSON array found in AI response")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            # Fallback: try to extract skills using simple parsing
            return self._fallback_skill_extraction(response)
        except Exception as e:
            logger.error(f"Unexpected error parsing AI response: {e}")
            return []
    
    def _fallback_skill_extraction(self, response: str) -> List[str]:
        """Fallback method to extract skills if JSON parsing fails."""
        # Simple fallback: look for lines that might be skills
        lines = response.split('\n')
        skills = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and obvious non-skills
            if line and len(line) < 50 and not line.startswith(('Here', 'Based', 'The', 'Skills')):
                # Remove common prefixes
                if line.startswith(('- ', '* ', '• ')):
                    line = line[2:].strip()
                if line.startswith(tuple('0123456789')):
                    line = line.split('.', 1)[-1].strip()
                
                if line:
                    skills.append(line.title())
        
        return skills[:20]  # Conservative limit for fallback
    
    def _track_extracted_skills(self, skills: List[str]):
        """Track extracted skills for analytics."""
        current_month = datetime.now().strftime('%Y-%m')
        
        for skill in skills:
            self.ai_skill_counter[skill] += 1
            self.ai_monthly_skill_data[skill][current_month] += 1
    
    def get_skill_analytics(self) -> Dict[str, Any]:
        """Get analytics about extracted skills."""
        return {
            "total_unique_skills": len(self.ai_skill_counter),
            "total_extractions": sum(self.ai_skill_counter.values()),
            "top_skills": dict(self.ai_skill_counter.most_common(20)),
            "service_type": self.service_type,
            "model": self.model_name
        }
    
    def get_trending_skills_chart_data(self) -> Dict[str, Any]:
        """Get chart data for trending AI-extracted skills over time."""
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
            'extraction_method': 'AI (Azure OpenAI)'
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
    
    def get_ai_skills_stats(self) -> List[Dict[str, Any]]:
        """Get AI skills statistics for display."""
        skills_list = []
        for skill, count in self.ai_skill_counter.most_common():
            skills_list.append({
                'skill': skill,
                'count': count,
                'documents': len(self.ai_skill_documents.get(skill, []))
            })
        return skills_list

# Global AI extractor instance
ai_extractor = AISkillExtractor()