#!/usr/bin/env python3
"""
Solutions for handling corrupted PDFs
"""

import os
import re
from typing import List, Set

def create_corrupted_skill_mapper():
    """Create a mapping of corrupted skill names to correct ones"""
    return {
        # Programming Languages - corrupted versions
        'jv': 'Java',
        'jva': 'Java', 
        'pyhon': 'Python',
        'pyhn': 'Python',
        'jscrp': 'JavaScript',
        'jvscrp': 'JavaScript',
        'ypescrp': 'TypeScript',
        'ypescrip': 'TypeScript',
        'php': 'PHP',  # This one actually worked
        'crp': 'C++',
        'c++': 'C++',
        'cshp': 'C#',
        'rby': 'Ruby',
        'go': 'Go',
        'rs': 'Rust',
        'swi': 'Swift',
        'koin': 'Kotlin',
        'scl': 'Scala',
        
        # Frameworks & Libraries
        'rek': 'React',
        'rec': 'React',
        'ngr': 'Angular',
        'vejs': 'Vue.js',
        'sprig': 'Spring',
        'sprig bo': 'Spring Boot',
        'djngo': 'Django',
        'fsk': 'Flask',
        'lrve': 'Laravel',
        'nodjs': 'Node.js',
        'expess': 'Express.js',
        'nexjs': 'Next.js',
        'nuxjs': 'Nuxt.js',
        
        # Databases
        'mysq': 'MySQL',
        'posgresq': 'PostgreSQL',
        'posges': 'PostgreSQL',
        'mongodb': 'MongoDB',
        'mongo': 'MongoDB',
        'redis': 'Redis',
        'cssnd': 'Cassandra',
        'sq seve': 'SQL Server',
        'oce': 'Oracle',
        
        # Cloud & DevOps
        'ws': 'AWS',
        'zre': 'Azure',
        'gcp': 'GCP',
        'google cod': 'Google Cloud',
        'docke': 'Docker',
        'dokr': 'Docker',
        'kbernes': 'Kubernetes',
        'k8s': 'Kubernetes',
        'jenkins': 'Jenkins',
        'gi': 'Git',
        'github': 'GitHub',
        'gib': 'GitLab',
        'cicd': 'CI/CD',
        'ci/cd': 'CI/CD',
        
        # Web Technologies
        'hm': 'HTML',
        'css': 'CSS',
        'scss': 'SCSS',
        'sss': 'SASS',
        'boosp': 'Bootstrap',
        'iwind': 'Tailwind CSS',
        'jqery': 'jQuery',
        
        # Tools & IDEs
        'vs code': 'Visual Studio Code',
        'vscoe': 'Visual Studio Code',
        'visu sudo': 'Visual Studio',
        'inelijidea': 'IntelliJ IDEA',
        'ecipse': 'Eclipse',
        'vim': 'Vim',
        'emcs': 'Emacs',
        
        # Norwegian specific terms (job posting language)
        'bckend-viker': 'backend developer',
        'frontend-viker': 'frontend developer',
        'fulsk-viker': 'fullstack developer',
        'progrmmerer': 'programmer',
        'viker': 'developer',
        'systemviker': 'system developer',
        'webviker': 'web developer',
        
        # Common corrupted patterns
        'res p': 'REST API',
        'rest pi': 'REST API',
        'grphq': 'GraphQL',
        'json': 'JSON',
        'xm': 'XML',
        'yml': 'YAML',
        'microservices': 'Microservices',
        'gi': 'Agile',
        'scrm': 'Scrum',
        'knbn': 'Kanban',
        'devops': 'DevOps',
    }

def extract_skills_from_corrupted_text(text: str) -> List[str]:
    """Extract skills from corrupted PDF text using fuzzy matching"""
    found_skills = set()
    corrupted_mapper = create_corrupted_skill_mapper()
    
    # Normalize text
    text_lower = text.lower()
    text_normalized = ' '.join(text.split())
    
    print(f"🔍 Searching for corrupted skill patterns...")
    
    # Method 1: Direct corrupted pattern matching
    for corrupted_pattern, real_skill in corrupted_mapper.items():
        # Use word boundaries for better matching
        pattern = r'\b' + re.escape(corrupted_pattern) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(real_skill)
            print(f"  ✅ Found '{corrupted_pattern}' → '{real_skill}'")
    
    # Method 2: Fuzzy pattern matching for partially corrupted words
    skill_fragments = {
        'spring': 'Spring Boot',
        'boot': 'Spring Boot', 
        'react': 'React',
        'angular': 'Angular',
        'python': 'Python',
        'javascript': 'JavaScript',
        'typescript': 'TypeScript',
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        'mysql': 'MySQL',
        'postgresql': 'PostgreSQL',
        'mongodb': 'MongoDB',
        'backend': 'Backend Development',
        'frontend': 'Frontend Development',
        'fullstack': 'Full Stack Development',
        'api': 'API Development',
        'rest': 'REST API',
        'json': 'JSON',
        'xml': 'XML',
        'git': 'Git',
        'github': 'GitHub',
        'gitlab': 'GitLab',
        'azure': 'Azure',
        'aws': 'AWS',
        'cloud': 'Cloud Computing',
        'devops': 'DevOps',
        'agile': 'Agile',
        'scrum': 'Scrum',
        'microservice': 'Microservices',
    }
    
    print(f"🔍 Searching for skill fragments...")
    for fragment, skill in skill_fragments.items():
        if fragment in text_lower and skill not in found_skills:
            found_skills.add(skill)
            print(f"  ✅ Found fragment '{fragment}' → '{skill}'")
    
    # Method 3: Look for Norwegian job-related terms that indicate tech skills
    norwegian_tech_indicators = {
        'utvikling': 'Software Development',
        'programmering': 'Programming', 
        'systemutvikling': 'System Development',
        'webutvikling': 'Web Development',
        'applikasjonsutvikling': 'Application Development',
        'backend': 'Backend Development',
        'frontend': 'Frontend Development',
        'database': 'Database Management',
        'integrasjon': 'System Integration',
        'arkitektur': 'Software Architecture',
        'testing': 'Software Testing',
        'kvalitetssikring': 'Quality Assurance',
        'sikkerhet': 'Security',
        'skyløsninger': 'Cloud Solutions',
    }
    
    print(f"🔍 Searching for Norwegian tech indicators...")
    for norwegian_term, english_skill in norwegian_tech_indicators.items():
        if norwegian_term in text_lower and english_skill not in found_skills:
            found_skills.add(english_skill)
            print(f"  ✅ Found Norwegian term '{norwegian_term}' → '{english_skill}'")
    
    return list(found_skills)

def test_corrupted_extraction():
    """Test the corrupted text extraction"""
    filepath = "uploads/Senior_backend-utvikler_-_arbeidsplassen.no_extracted_text.txt"
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        corrupted_text = f.read()
    
    print("🔧 CORRUPTED PDF SKILL EXTRACTION")
    print("=" * 60)
    print(f"📄 Text length: {len(corrupted_text)} characters")
    
    # Extract skills using corrupted text methods
    skills = extract_skills_from_corrupted_text(corrupted_text)
    
    print(f"\n📊 RESULTS:")
    print(f"  - Skills found: {len(skills)}")
    print(f"  - Skills: {', '.join(sorted(skills))}")
    
    return skills

if __name__ == "__main__":
    test_corrupted_extraction()
