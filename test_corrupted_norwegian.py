#!/usr/bin/env python3
"""
Test AI extraction on real Norwegian document with PDF corruption issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_skills import AISkillExtractor

def test_corrupted_norwegian_document():
    """Test AI extraction on the actual corrupted Norwegian job description."""
    
    # Initialize AI extractor
    extractor = AISkillExtractor()
    
    if not extractor.client:
        print("❌ AI client not configured.")
        return
    
    print(f"✅ AI Service: {extractor.service_type}")
    print(f"✅ Model: {extractor.model_name}")
    print("-" * 60)
    
    # Read the corrupted Norwegian document
    try:
        with open('/Users/a.abdurihim/Documents/Code/get-skills/uploads/Senior_backend-utvikler_-_arbeidsplassen.no_extracted_text.txt', 'r', encoding='utf-8') as f:
            corrupted_text = f.read()
        
        print("🧪 Testing with actual corrupted Norwegian document")
        print("📄 Document: Senior_backend-utvikler_-_arbeidsplassen.no.pdf")
        print(f"📏 Text length: {len(corrupted_text)} characters")
        print("-" * 60)
        
        # Extract skills using AI
        skills, metadata = extractor.extract_skills_from_text(
            corrupted_text, 
            "job_description"
        )
        
        if skills:
            print(f"✅ AI extracted {len(skills)} skills from corrupted text:")
            
            # Categorize and display skills
            technical_skills = []
            soft_skills = []
            
            soft_skill_keywords = [
                'communication', 'leadership', 'teamwork', 'problem solving',
                'analytical', 'creative', 'adaptability', 'flexibility',
                'collaboration', 'interpersonal', 'initiative', 'responsibility',
                'kommunikasjon', 'lederskap', 'samarbeid', 'problemløsning',
                'analytisk', 'kreativ', 'tilpasningsevne', 'fleksibilitet'
            ]
            
            for skill in skills:
                is_soft = any(keyword in skill.lower() for keyword in soft_skill_keywords)
                if is_soft:
                    soft_skills.append(skill)
                else:
                    technical_skills.append(skill)
            
            if technical_skills:
                print("\n📱 Technical Skills:")
                for skill in sorted(technical_skills):
                    print(f"   • {skill}")
            
            if soft_skills:
                print("\n🧠 Soft Skills:")
                for skill in sorted(soft_skills):
                    print(f"   • {skill}")
            
            print(f"\n📊 Extraction Statistics:")
            print(f"   • Total Skills: {len(skills)}")
            print(f"   • Technical: {len(technical_skills)}")
            print(f"   • Soft Skills: {len(soft_skills)}")
            print(f"   • AI Service: {metadata.get('ai_service', 'Unknown')}")
            print(f"   • Model: {metadata.get('model', 'Unknown')}")
            
        else:
            print("❌ No skills extracted from corrupted document")
        
        # Now compare with pattern matching results
        print("\n" + "="*60)
        print("🔍 Comparison with Pattern Matching Results")
        print("="*60)
        
        try:
            import json
            with open('/Users/a.abdurihim/Documents/Code/get-skills/uploads/Senior_backend-utvikler_-_arbeidsplassen.no_skill_matches.json', 'r', encoding='utf-8') as f:
                pattern_results = json.load(f)
            
            print(f"📊 Pattern matching found {len(pattern_results)} skills:")
            for match in pattern_results:
                print(f"   • {match['skill']} ({match['method']})")
            
            print(f"\n📈 Results Comparison:")
            print(f"   • AI Extraction: {len(skills)} skills")
            print(f"   • Pattern Matching: {len(pattern_results)} skills")
            
            if len(skills) > len(pattern_results):
                improvement = len(skills) - len(pattern_results)
                print(f"   • AI found {improvement} more skills than pattern matching!")
            
        except Exception as e:
            print(f"❌ Error reading pattern matching results: {e}")
            
    except Exception as e:
        print(f"❌ Error reading document: {e}")

if __name__ == "__main__":
    test_corrupted_norwegian_document()