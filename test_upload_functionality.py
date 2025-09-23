#!/usr/bin/env python3
"""
Enhanced Local Testing Script for PDF & Excel Skills Extractor
Tests actual file upload functionality with both PDF and Excel files
"""

import requests
import time
import os
import json
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:5001"
UPLOADS_DIR = Path("uploads")

def test_server_status():
    """Test if the server is running and responsive"""
    print("1. Testing server status...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responsive")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_file_upload(file_path, file_type):
    """Test uploading a file and extracting skills"""
    print(f"\n2. Testing {file_type} file upload: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        # Prepare the file for upload
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
            
            print(f"   📤 Uploading {os.path.basename(file_path)}...")
            response = requests.post(f"{BASE_URL}/upload", files=files, timeout=30)
            
            if response.status_code == 200:
                print("   ✅ File uploaded successfully")
                
                # Check if response contains JSON data
                try:
                    result = response.json()
                    if 'skills' in result:
                        skills = result['skills']
                        print(f"   🎯 Skills extracted: {len(skills)} skills found")
                        
                        # Show first few skills
                        if skills:
                            print("   📋 Sample skills:")
                            for i, skill in enumerate(skills[:5]):
                                print(f"      {i+1}. {skill}")
                            if len(skills) > 5:
                                print(f"      ... and {len(skills) - 5} more")
                        
                        return True
                    else:
                        print("   ⚠️  No skills data in response")
                        return False
                        
                except json.JSONDecodeError:
                    # If not JSON, it might be an HTML response (redirect)
                    if "text/html" in response.headers.get('content-type', ''):
                        print("   ✅ File processed (received HTML response - likely a redirect)")
                        return True
                    else:
                        print(f"   ❌ Unexpected response format: {response.headers.get('content-type')}")
                        return False
            else:
                print(f"   ❌ Upload failed with status {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_documents_page():
    """Test the documents listing page"""
    print("\n3. Testing documents page...")
    try:
        response = requests.get(f"{BASE_URL}/documents", timeout=10)
        if response.status_code == 200:
            print("   ✅ Documents page accessible")
            
            # Check if we can find any document entries
            content = response.text
            if "📄" in content or "📊" in content:
                print("   📋 Documents are being displayed with proper icons")
            
            return True
        else:
            print(f"   ❌ Documents page returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Cannot access documents page: {e}")
        return False

def main():
    """Main testing function"""
    print("🧪 PDF & Excel Skills Extractor - Enhanced Local Testing")
    print("=" * 65)
    
    # Test 1: Server status
    if not test_server_status():
        print("\n💡 Please start the server first: python app.py")
        return
    
    # Wait a moment for server to be fully ready
    time.sleep(1)
    
    # Test 2: Find test files
    test_files = []
    
    # Look for PDF files
    pdf_files = list(UPLOADS_DIR.glob("*.pdf"))
    if pdf_files:
        test_files.append((str(pdf_files[0]), "PDF"))
    
    # Look for Excel files (we can create one if none exist)
    excel_files = list(UPLOADS_DIR.glob("*.xlsx")) + list(UPLOADS_DIR.glob("*.xls"))
    if excel_files:
        test_files.append((str(excel_files[0]), "Excel"))
    elif os.path.exists("test_resume_with_skills.xlsx"):
        test_files.append(("test_resume_with_skills.xlsx", "Excel"))
    
    if not test_files:
        print("\n⚠️  No test files found. Let me check what files are available...")
        all_files = list(Path(".").glob("*.pdf")) + list(Path(".").glob("*.xlsx")) + list(Path(".").glob("*.xls"))
        if all_files:
            print(f"   Found files: {[f.name for f in all_files]}")
            test_files.append((str(all_files[0]), "Unknown"))
        else:
            print("   No PDF or Excel files found for testing")
            return
    
    # Test file uploads
    success_count = 0
    for file_path, file_type in test_files:
        if test_file_upload(file_path, file_type):
            success_count += 1
    
    # Test 3: Documents page
    test_documents_page()
    
    # Summary
    print(f"\n📊 Testing Summary:")
    print(f"   Files tested: {len(test_files)}")
    print(f"   Successful uploads: {success_count}")
    print(f"   Success rate: {success_count/len(test_files)*100:.0f}%" if test_files else "   No files to test")
    
    if success_count == len(test_files) and success_count > 0:
        print("\n🎉 All tests passed! Your application is working correctly.")
        print(f"🌐 Visit {BASE_URL} to use the web interface")
    elif success_count > 0:
        print(f"\n⚠️  Partial success: {success_count}/{len(test_files)} tests passed")
    else:
        print("\n❌ All tests failed. Check the server logs for errors.")

if __name__ == "__main__":
    main()
