"""
Monthly Skills Analysis Module

This module provides comprehensive monthly analysis of uploaded files,
extracting insights about skill trends, soft skills requirements, and
generating detailed reports for stakeholders.
"""

import json
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple
import logging
from dataclasses import dataclass, asdict

# Import existing modules
from ai_skills import ai_extractor
from skills import tech_skills

logger = logging.getLogger(__name__)

@dataclass
class MonthlyAnalysisReport:
    """Data class for monthly analysis report."""
    analysis_month: str
    total_documents: int
    total_resumes: int
    total_job_descriptions: int
    
    # Skills statistics
    top_technical_skills: List[Dict[str, Any]]
    top_soft_skills: List[Dict[str, Any]]
    emerging_skills: List[Dict[str, Any]]
    declining_skills: List[Dict[str, Any]]
    
    # AI vs Pattern matching comparison
    ai_extraction_stats: Dict[str, Any]
    pattern_matching_stats: Dict[str, Any]
    
    # Industry insights
    skill_gap_analysis: Dict[str, Any]
    soft_skills_trends: Dict[str, Any]
    recommendations: List[str]
    
    # Metadata
    generated_at: str
    analysis_period: Dict[str, str]

class MonthlySkillsAnalyzer:
    """Comprehensive monthly skills analysis system."""
    
    def __init__(self):
        """Initialize the monthly analyzer."""
        self.soft_skills = {
            'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
            'creativity', 'adaptability', 'time management', 'project management',
            'collaboration', 'analytical thinking', 'decision making', 'conflict resolution',
            'emotional intelligence', 'negotiation', 'presentation', 'mentoring',
            'strategic thinking', 'innovation', 'customer service', 'interpersonal skills'
        }
        
        self.technical_skill_categories = {
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'swift'],
            'web_development': ['react', 'angular', 'vue', 'html', 'css', 'node.js', 'express'],
            'databases': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'data_science': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'spark'],
            'devops': ['jenkins', 'git', 'ci/cd', 'ansible', 'helm', 'prometheus']
        }
    
    def generate_monthly_report(self, target_month: str = None) -> MonthlyAnalysisReport:
        """
        Generate comprehensive monthly analysis report.
        
        Args:
            target_month: Month to analyze in YYYY-MM format. If None, analyzes previous month.
            
        Returns:
            MonthlyAnalysisReport object with complete analysis
        """
        if target_month is None:
            # Default to previous month
            last_month = datetime.now().replace(day=1) - timedelta(days=1)
            target_month = last_month.strftime('%Y-%m')
        
        logger.info(f"Generating monthly analysis report for {target_month}")
        
        # Get data for the target month
        month_data = self._extract_month_data(target_month)
        
        # Analyze skills
        technical_skills = self._analyze_technical_skills(month_data)
        soft_skills_analysis = self._analyze_soft_skills(month_data)
        
        # Compare with previous month for trends
        trends = self._analyze_trends(target_month, month_data)
        
        # Generate insights and recommendations
        insights = self._generate_insights(month_data, technical_skills, soft_skills_analysis)
        
        # Create report
        report = MonthlyAnalysisReport(
            analysis_month=target_month,
            total_documents=month_data['total_documents'],
            total_resumes=month_data['resumes_count'],
            total_job_descriptions=month_data['job_descriptions_count'],
            
            top_technical_skills=technical_skills['top_skills'],
            top_soft_skills=soft_skills_analysis['top_soft_skills'],
            emerging_skills=trends['emerging_skills'],
            declining_skills=trends['declining_skills'],
            
            ai_extraction_stats=month_data['ai_stats'],
            pattern_matching_stats=month_data['pattern_stats'],
            
            skill_gap_analysis=insights['skill_gaps'],
            soft_skills_trends=soft_skills_analysis['trends'],
            recommendations=insights['recommendations'],
            
            generated_at=datetime.now().isoformat(),
            analysis_period={
                'start': f"{target_month}-01",
                'end': self._get_month_end(target_month)
            }
        )
        
        # Save report
        self._save_monthly_report(report)
        
        return report
    
    def _extract_month_data(self, target_month: str) -> Dict[str, Any]:
        """Extract all data for the target month."""
        month_data = {
            'total_documents': 0,
            'resumes_count': 0,
            'job_descriptions_count': 0,
            'pattern_skills': Counter(),
            'ai_skills': Counter(),
            'documents': [],
            'ai_stats': {},
            'pattern_stats': {}
        }
        
        # Import here to avoid circular imports
        try:
            from app import processed_documents
        except ImportError:
            # Fallback if processed_documents not available
            processed_documents = {}
        
        # Analyze processed documents from pattern matching
        for filename, doc_data in processed_documents.items():
            doc_date = doc_data.get('file_date', doc_data.get('upload_date', ''))
            if doc_date.startswith(target_month):
                month_data['total_documents'] += 1
                month_data['documents'].append(doc_data)
                
                # Categorize document type
                if self._is_resume(filename):
                    month_data['resumes_count'] += 1
                else:
                    month_data['job_descriptions_count'] += 1
                
                # Add pattern matching skills
                for skill in doc_data.get('skills_found', []):
                    month_data['pattern_skills'][skill] += 1
                
                # Add AI skills
                for skill in doc_data.get('ai_skills_found', []):
                    month_data['ai_skills'][skill] += 1
        
        # Get AI extraction statistics
        month_data['ai_stats'] = {
            'total_skills_extracted': len(month_data['ai_skills']),
            'unique_skills': len(set(month_data['ai_skills'].keys())),
            'avg_skills_per_document': len(month_data['ai_skills']) / max(month_data['total_documents'], 1),
            'service_type': ai_extractor.service_type,
            'model': ai_extractor.model_name
        }
        
        # Get pattern matching statistics
        month_data['pattern_stats'] = {
            'total_skills_extracted': len(month_data['pattern_skills']),
            'unique_skills': len(set(month_data['pattern_skills'].keys())),
            'avg_skills_per_document': len(month_data['pattern_skills']) / max(month_data['total_documents'], 1)
        }
        
        return month_data
    
    def _analyze_technical_skills(self, month_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical skills from the month's data."""
        # Combine AI and pattern matching results
        all_skills = Counter()
        all_skills.update(month_data['pattern_skills'])
        all_skills.update(month_data['ai_skills'])
        
        # Categorize skills
        categorized_skills = defaultdict(Counter)
        uncategorized_skills = Counter()
        
        for skill, count in all_skills.items():
            skill_lower = skill.lower()
            categorized = False
            
            for category, skill_list in self.technical_skill_categories.items():
                if any(tech_skill in skill_lower for tech_skill in skill_list):
                    categorized_skills[category][skill] = count
                    categorized = True
                    break
            
            if not categorized and skill_lower not in self.soft_skills:
                uncategorized_skills[skill] = count
        
        return {
            'top_skills': [{'skill': skill, 'count': count, 'percentage': round(count/max(sum(all_skills.values()), 1)*100, 2)} 
                          for skill, count in all_skills.most_common(20)],
            'categorized_skills': dict(categorized_skills),
            'uncategorized_technical': dict(uncategorized_skills.most_common(10)),
            'total_technical_skills': len(all_skills)
        }
    
    def _analyze_soft_skills(self, month_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze soft skills and their trends."""
        # Combine AI and pattern matching results
        all_skills = Counter()
        all_skills.update(month_data['pattern_skills'])
        all_skills.update(month_data['ai_skills'])
        
        # Extract soft skills
        soft_skills_found = Counter()
        for skill, count in all_skills.items():
            if skill.lower() in self.soft_skills or any(soft in skill.lower() for soft in self.soft_skills):
                soft_skills_found[skill] = count
        
        # Calculate soft skills ratio
        total_skills = sum(all_skills.values())
        soft_skills_total = sum(soft_skills_found.values())
        soft_skills_ratio = soft_skills_total / max(total_skills, 1)
        
        return {
            'top_soft_skills': [{'skill': skill, 'count': count, 'percentage': round(count/max(total_skills, 1)*100, 2)} 
                               for skill, count in soft_skills_found.most_common(10)],
            'soft_skills_ratio': round(soft_skills_ratio * 100, 2),
            'trends': {
                'most_demanded': soft_skills_found.most_common(5),
                'total_soft_skills_mentions': soft_skills_total,
                'documents_with_soft_skills': len([doc for doc in month_data['documents'] 
                                                 if any(skill.lower() in self.soft_skills 
                                                       for skill in doc.get('skills_found', []) + doc.get('ai_skills_found', []))])
            }
        }
    
    def _analyze_trends(self, target_month: str, month_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skill trends compared to previous month."""
        # Get previous month data
        target_date = datetime.strptime(target_month + '-01', '%Y-%m-%d')
        prev_month_date = target_date - timedelta(days=1)
        prev_month = prev_month_date.strftime('%Y-%m')
        
        prev_month_data = self._extract_month_data(prev_month)
        
        # Compare skills
        current_skills = Counter()
        current_skills.update(month_data['pattern_skills'])
        current_skills.update(month_data['ai_skills'])
        
        prev_skills = Counter()
        prev_skills.update(prev_month_data['pattern_skills'])
        prev_skills.update(prev_month_data['ai_skills'])
        
        # Find emerging and declining skills
        emerging_skills = []
        declining_skills = []
        
        for skill, current_count in current_skills.items():
            prev_count = prev_skills.get(skill, 0)
            if prev_count == 0 and current_count > 2:  # New skills with significant mentions
                emerging_skills.append({'skill': skill, 'count': current_count, 'change': 'NEW'})
            elif prev_count > 0:
                change_percent = ((current_count - prev_count) / prev_count) * 100
                if change_percent > 50 and current_count > prev_count:  # 50% increase
                    emerging_skills.append({'skill': skill, 'count': current_count, 'change': f'+{change_percent:.1f}%'})
                elif change_percent < -30:  # 30% decrease
                    declining_skills.append({'skill': skill, 'count': current_count, 'change': f'{change_percent:.1f}%'})
        
        return {
            'emerging_skills': sorted(emerging_skills, key=lambda x: x['count'], reverse=True)[:10],
            'declining_skills': sorted(declining_skills, key=lambda x: x['count'], reverse=True)[:10],
            'comparison_month': prev_month
        }
    
    def _generate_insights(self, month_data: Dict[str, Any], technical_skills: Dict[str, Any], soft_skills_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights and recommendations."""
        recommendations = []
        skill_gaps = {}
        
        # Analyze skill gaps between resumes and job descriptions
        resume_skills = Counter()
        job_desc_skills = Counter()
        
        for doc in month_data['documents']:
            skills = doc.get('skills_found', []) + doc.get('ai_skills_found', [])
            if self._is_resume(doc.get('filename', '')):
                resume_skills.update(skills)
            else:
                job_desc_skills.update(skills)
        
        # Find skills in high demand but low supply
        high_demand_skills = set(skill for skill, count in job_desc_skills.most_common(20))
        available_skills = set(skill for skill, count in resume_skills.most_common(20))
        
        skill_gaps = {
            'high_demand_low_supply': list(high_demand_skills - available_skills),
            'oversupplied_skills': list(available_skills - high_demand_skills),
            'balanced_skills': list(high_demand_skills & available_skills)
        }
        
        # Generate recommendations
        if len(skill_gaps['high_demand_low_supply']) > 0:
            recommendations.append(f"Skills in high demand but low supply: {', '.join(skill_gaps['high_demand_low_supply'][:5])}")
        
        if soft_skills_analysis['soft_skills_ratio'] < 15:
            recommendations.append("Consider emphasizing soft skills more in job requirements and resume reviews")
        
        if technical_skills['total_technical_skills'] > 50:
            recommendations.append("Diverse technical skill requirements suggest need for specialized roles")
        
        if month_data['ai_stats']['avg_skills_per_document'] < 5:
            recommendations.append("Consider improving skill extraction accuracy or document quality")
        
        return {
            'skill_gaps': skill_gaps,
            'recommendations': recommendations
        }
    
    def _is_resume(self, filename: str) -> bool:
        """Determine if a file is likely a resume based on filename."""
        resume_indicators = ['cv', 'resume', 'curriculum']
        return any(indicator in filename.lower() for indicator in resume_indicators)
    
    def _get_month_end(self, target_month: str) -> str:
        """Get the last day of the month."""
        year, month = map(int, target_month.split('-'))
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        last_day = next_month - timedelta(days=1)
        return last_day.strftime('%Y-%m-%d')
    
    def _save_monthly_report(self, report: MonthlyAnalysisReport):
        """Save the monthly report to storage."""
        try:
            # Convert to dictionary
            report_dict = asdict(report)
            
            # Save to local file (in production, this would go to Azure Storage)
            reports_dir = "monthly_reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            filename = f"{reports_dir}/monthly_analysis_{report.analysis_month}.json"
            with open(filename, 'w') as f:
                json.dump(report_dict, f, indent=2, default=str)
            
            logger.info(f"Monthly report saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save monthly report: {e}")
    
    def get_latest_report(self) -> Dict[str, Any]:
        """Get the most recent monthly report."""
        try:
            reports_dir = "monthly_reports"
            if not os.path.exists(reports_dir):
                return {}
            
            # Find the most recent report
            report_files = [f for f in os.listdir(reports_dir) if f.endswith('.json')]
            if not report_files:
                return {}
            
            latest_file = max(report_files)
            with open(os.path.join(reports_dir, latest_file), 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to load latest report: {e}")
            return {}
    
    def schedule_monthly_analysis(self):
        """
        Schedule monthly analysis (called by Azure Functions timer).
        This method is designed to be called automatically.
        """
        try:
            # Generate report for previous month
            report = self.generate_monthly_report()
            
            # Send notifications (implement as needed)
            self._send_monthly_report_notification(report)
            
            logger.info(f"Scheduled monthly analysis completed for {report.analysis_month}")
            return True
            
        except Exception as e:
            logger.error(f"Scheduled monthly analysis failed: {e}")
            return False
    
    def _send_monthly_report_notification(self, report: MonthlyAnalysisReport):
        """Send notification about the monthly report (placeholder for future implementation)."""
        # This could send emails, Teams messages, or push notifications
        logger.info(f"Monthly report generated for {report.analysis_month}: {report.total_documents} documents analyzed")

# Global analyzer instance
monthly_analyzer = MonthlySkillsAnalyzer()