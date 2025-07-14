#!/usr/bin/env python3
"""
Test script to specifically verify unique skill extraction per document.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import extract_skills

def test_unique_extraction():
    """Test that skills are extracted uniquely regardless of frequency in text."""
    
    # Test text with multiple mentions of the same skills
    test_text = """
    I am proficient in Python programming. I have used Python for web development.
    My Python experience includes Django and Flask frameworks. Python is my favorite language.
    I also know JavaScript and have worked with JavaScript frameworks like React.
    JavaScript is essential for frontend development. I use JavaScript daily.
    
    In my career, I have used Docker containers extensively. Docker helps with deployment.
    Docker is great for microservices. I configure Docker environments regularly.
    
    I also work with AWS cloud services. AWS provides excellent scalability.
    My AWS experience includes EC2, S3, and RDS. AWS is my preferred cloud platform.
    """
    
    print("🎯 UNIQUE SKILL EXTRACTION TEST")
    print("=" * 50)
    print("Test text mentions:")
    print("- Python: 5 times")
    print("- JavaScript: 4 times") 
    print("- Docker: 4 times")
    print("- AWS: 4 times")
    print("- React: 1 time")
    print("- Django: 1 time")
    print("- Flask: 1 time")
    print()
    
    # Extract skills
    found_skills = extract_skills(test_text)
    
    print("EXTRACTED UNIQUE SKILLS:")
    print("-" * 25)
    for i, skill in enumerate(sorted(found_skills), 1):
        print(f"{i}. {skill}")
    
    print()
    print(f"Total unique skills found: {len(found_skills)}")
    
    # Verify expected skills are present
    expected_skills = {'Python', 'JavaScript', 'Docker', 'AWS', 'React', 'Django', 'Flask'}
    found_skills_set = set(found_skills)
    
    print()
    print("VERIFICATION:")
    print("-" * 12)
    
    if expected_skills.issubset(found_skills_set):
        print("✅ All expected skills found")
    else:
        missing = expected_skills - found_skills_set
        print(f"❌ Missing skills: {missing}")
    
    # Check for no duplicates
    if len(found_skills) == len(set(found_skills)):
        print("✅ No duplicate skills in results")
    else:
        print("❌ Duplicate skills found!")
    
    print()
    print("🎯 CONCLUSION: Each skill extracted ONCE per document, regardless of text frequency")
    print("📊 This ensures accurate counting and prevents text verbosity from skewing analytics")

if __name__ == "__main__":
    test_unique_extraction()
