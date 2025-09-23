#!/usr/bin/env python3
"""
Test script to verify Excel skills extraction functionality.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append('/Users/a.abdurihim/Documents/Code/get-skills')

# Import required functions from app.py
from app import extract_text_from_excel, extract_skills, get_excel_creation_date, get_file_type

def test_excel_extraction():
    """Test Excel text extraction and skill finding."""
    
    excel_file_path = "/Users/a.abdurihim/Documents/Code/get-skills/test_resume_with_skills.xlsx"
    
    if not os.path.exists(excel_file_path):
        print(f"Error: Test Excel file not found at {excel_file_path}")
        return False
    
    print("Testing Excel Skills Extraction")
    print("=" * 40)
    
    # Read the Excel file
    with open(excel_file_path, 'rb') as f:
        file_content = f.read()
    
    # Test file type detection
    file_type = get_file_type("test_resume_with_skills.xlsx")
    print(f"Detected file type: {file_type}")
    
    # Test text extraction
    print("\n1. Testing text extraction...")
    extracted_text = extract_text_from_excel(file_content, "test_resume_with_skills.xlsx")
    
    if extracted_text:
        print(f"✅ Text extraction successful!")
        print(f"Extracted text length: {len(extracted_text)} characters")
        print(f"First 200 characters: {extracted_text[:200]}...")
    else:
        print("❌ Text extraction failed!")
        return False
    
    # Test skill extraction
    print("\n2. Testing skill extraction...")
    found_skills = extract_skills(extracted_text)
    
    if found_skills:
        print(f"✅ Skills extraction successful!")
        print(f"Found {len(found_skills)} skills:")
        for skill in sorted(found_skills):
            print(f"  - {skill}")
    else:
        print("❌ No skills found!")
        return False
    
    # Test metadata extraction
    print("\n3. Testing metadata extraction...")
    creation_date = get_excel_creation_date(file_content, "test_resume_with_skills.xlsx")
    
    if creation_date:
        print(f"✅ Creation date extracted: {creation_date}")
    else:
        print("ℹ️  No creation date found (this is normal for new files)")
    
    print("\n" + "=" * 40)
    print("✅ Excel extraction test completed successfully!")
    return True

def test_existing_pdf():
    """Test that PDF functionality still works."""
    
    # Look for existing PDF files
    uploads_dir = "/Users/a.abdurihim/Documents/Code/get-skills/uploads"
    
    if os.path.exists(uploads_dir):
        pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
        
        if pdf_files:
            print(f"\nTesting existing PDF file: {pdf_files[0]}")
            
            pdf_path = os.path.join(uploads_dir, pdf_files[0])
            file_type = get_file_type(pdf_files[0])
            print(f"PDF file type detection: {file_type}")
            
            # Test that our new code doesn't break PDF processing
            if file_type == 'pdf':
                print("✅ PDF file type detection still works!")
            else:
                print("❌ PDF file type detection broken!")
                return False
    
    return True

if __name__ == "__main__":
    print("Skills Extractor - Excel Integration Test")
    print("=========================================\n")
    
    success = True
    
    # Test Excel functionality
    success &= test_excel_extraction()
    
    # Test PDF functionality (backwards compatibility)
    success &= test_existing_pdf()
    
    if success:
        print("\n🎉 All tests passed! Excel integration is working correctly.")
        print("\nYou can now:")
        print("1. Start the Flask app: python app.py")
        print("2. Upload Excel files (.xlsx, .xls) in addition to PDF files")
        print("3. Skills will be extracted from both file types")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
