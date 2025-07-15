#!/usr/bin/env python3
"""
Test extraction on the new Senior backend developer PDF
"""

import os
import re
import PyPDF2
from collections import Counter
import json

# Import the skills list
from skills import tech_skills

def extract_text_from_pdf(filepath):
    """Extract text content from a PDF file."""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # Clean up common PDF extraction issues
            # Remove excessive whitespace while preserving word boundaries
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with single space
            text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
            text = text.strip()
            
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_skills_debug(text):
    """Extract technology skills with debugging information."""
    found_skills = set()
    
    # Normalize text: remove excessive whitespace and line breaks
    normalized_text = ' '.join(text.split()).lower()
    
    # Also create a version without spaces for compound skills
    no_spaces_text = re.sub(r'\s+', '', text.lower())
    
    print(f"\n📄 Original text length: {len(text)} characters")
    print(f"📄 Normalized text length: {len(normalized_text)} characters")
    print(f"📄 First 1000 characters of normalized text:\n{normalized_text[:1000]}...")
    print(f"\n🔍 Checking {len(tech_skills)} skills...")
    
    matches_found = []
    
    for skill in tech_skills:
        skill_lower = skill.lower()
        skill_found = False
        match_method = ""
        match_context = ""
        
        # Method 1: Standard word boundary matching (for simple skills)
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        match = re.search(pattern, normalized_text)
        if match:
            skill_found = True
            match_method = "Standard"
            match_context = normalized_text[max(0, match.start()-30):match.end()+30]
        
        # Method 2: Flexible matching for compound skills
        if not skill_found:
            flexible_pattern = re.escape(skill_lower)
            flexible_pattern = flexible_pattern.replace(r'\.', r'[\.\s]*')
            flexible_pattern = flexible_pattern.replace(r'\+', r'[\+\s]*')
            flexible_pattern = flexible_pattern.replace(r'\#', r'[\#\s]*')
            flexible_pattern = flexible_pattern.replace(r'\s', r'\s*')
            
            match = re.search(r'\b' + flexible_pattern + r'\b', normalized_text)
            if match:
                skill_found = True
                match_method = "Flexible"
                match_context = normalized_text[max(0, match.start()-30):match.end()+30]
        
        # Method 3: No-spaces matching for fragmented text
        if not skill_found:
            skill_no_spaces = re.sub(r'[\s\.\+\#-]', '', skill_lower)
            if len(skill_no_spaces) > 2 and skill_no_spaces in no_spaces_text:
                skill_found = True
                match_method = "No-spaces"
                start_idx = no_spaces_text.find(skill_no_spaces)
                match_context = no_spaces_text[max(0, start_idx-30):start_idx+len(skill_no_spaces)+30]
        
        if skill_found:
            found_skills.add(skill)
            matches_found.append({
                'skill': skill,
                'method': match_method,
                'context': match_context.strip()
            })
    
    # Check aliases
    skill_aliases = {
        'js': 'JavaScript',
        'ts': 'TypeScript', 
        'nodejs': 'Node.js',
        'reactjs': 'React',
        'vuejs': 'Vue.js',
        'nextjs': 'Next.js',
        'nuxtjs': 'Nuxt.js',
        'dotnet': 'ASP.NET',
        '.net': 'ASP.NET',
        'csharp': 'C#',
        'cplusplus': 'C++',
        'ai': 'Artificial Intelligence',
        'ml': 'Machine Learning',
        'dl': 'Deep Learning',
        'k8s': 'Kubernetes',
        'aws': 'AWS',
        'gcp': 'Google Cloud',
        'azure': 'Azure',
        'vscode': 'Visual Studio Code',
        'vs code': 'Visual Studio Code',
        'sql server': 'SQL Server',
        'postgresql': 'PostgreSQL',
        'mongo': 'MongoDB',
        'redis': 'Redis',
        'docker': 'Docker',
        'git': 'Git',
        'github': 'GitHub',
        'gitlab': 'GitLab',
        'rest': 'REST API',
        'api': 'API Development',
        'ci/cd': 'CI/CD',
        'cicd': 'CI/CD'
    }
    
    for alias, skill_name in skill_aliases.items():
        if skill_name not in found_skills:
            alias_pattern = r'\b' + re.escape(alias) + r'\b'
            match = re.search(alias_pattern, normalized_text)
            if match:
                found_skills.add(skill_name)
                matches_found.append({
                    'skill': skill_name,
                    'method': 'Alias',
                    'context': normalized_text[max(0, match.start()-30):match.end()+30].strip()
                })
    
    print(f"\n✅ Found {len(found_skills)} skills:")
    for match in matches_found:
        print(f"  - {match['skill']} ({match['method']}): '{match['context']}'")
    
    return list(found_skills), matches_found

def analyze_new_pdf():
    """Analyze the new Senior backend developer PDF."""
    pdf_path = "uploads/Senior_backend-utvikler_-_arbeidsplassen.no.pdf"
    
    print(f"\n📋 Analyzing: {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("❌ Could not extract text from PDF")
        return
    
    # Save extracted text for manual review
    text_file = pdf_path.replace('.pdf', '_extracted_text.txt')
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"💾 Extracted text saved to: {text_file}")
    
    skills, matches = extract_skills_debug(text)
    
    # Save skill matches for review
    if matches:
        matches_file = pdf_path.replace('.pdf', '_skill_matches.json')
        with open(matches_file, 'w', encoding='utf-8') as f:
            json.dump(matches, f, indent=2)
        print(f"💾 Skill matches saved to: {matches_file}")
    
    print(f"\n📊 Summary for {pdf_path}:")
    print(f"  - Text length: {len(text)} chars")
    print(f"  - Skills found: {len(skills)}")
    print(f"  - Skills: {', '.join(skills) if skills else 'None'}")
    
    # Check for common Norwegian words that might indicate language issues
    norwegian_indicators = ['utvikler', 'erfaring', 'kompetanse', 'teknologi', 'utvikling', 'ansvar', 'krav']
    found_norwegian = [word for word in norwegian_indicators if word in text.lower()]
    if found_norwegian:
        print(f"\n🇳🇴 Norwegian content detected: {', '.join(found_norwegian)}")
        print("This might be a Norwegian job description - skills might be in Norwegian!")
    
    return skills, text

if __name__ == "__main__":
    print("🔍 Testing New PDF Skill Extraction")
    print("=" * 60)
    analyze_new_pdf()
