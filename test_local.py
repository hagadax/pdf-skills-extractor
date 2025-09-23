#!/usr/bin/env python3
"""
Local testing script for PDF & Excel Skills Extractor
Tests file upload functionality via HTTP requests
"""

import requests
import os

def test_file_upload(file_path, server_url="http://127.0.0.1:5001"):
    """Test file upload to the Flask application."""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    filename = os.path.basename(file_path)
    file_type = "Excel" if filename.endswith(('.xlsx', '.xls')) else "PDF"
    
    print(f"\n📁 Testing {file_type} file upload: {filename}")
    print("-" * 50)
    
    try:
        # Prepare the file for upload
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/octet-stream')}
            
            # Send POST request to upload endpoint
            response = requests.post(f"{server_url}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"✅ Upload successful!")
                print(f"📄 Message: {result.get('message', 'No message')}")
                
                skills = result.get('skills', [])
                if skills:
                    print(f"🎯 Found {len(skills)} skills:")
                    for i, skill in enumerate(sorted(skills), 1):
                        print(f"   {i:2d}. {skill}")
                else:
                    print("ℹ️  No skills found")
                
                return True
            else:
                print(f"❌ Upload failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {server_url}")
        print("   Make sure the Flask app is running!")
        return False
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def check_server_status(server_url="http://127.0.0.1:5001"):
    """Check if the server is running."""
    try:
        response = requests.get(server_url)
        if response.status_code == 200:
            print(f"✅ Server is running at {server_url}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {server_url}")
        return False

def test_api_endpoints(server_url="http://127.0.0.1:5001"):
    """Test API endpoints."""
    try:
        # Test skills API
        response = requests.get(f"{server_url}/api/skills")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Skills API: {data.get('total_skills', 0)} unique skills tracked")
        
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    print("🧪 PDF & Excel Skills Extractor - Local Testing")
    print("=" * 55)
    
    server_url = "http://127.0.0.1:5001"
    
    # Check if server is running
    print("1. Checking server status...")
    if not check_server_status(server_url):
        print("\n💡 To start the server, run:")
        print("   python app.py")
        return
    
    # Test API endpoints
    print("\n2. Testing API endpoints...")
    test_api_endpoints(server_url)
    
    # Test file uploads
    print("\n3. Testing file uploads...")
    
    test_files = [
        "/Users/a.abdurihim/Documents/Code/get-skills/test_resume_with_skills.xlsx",
    ]
    
    # Look for PDF files in uploads directory
    uploads_dir = "/Users/a.abdurihim/Documents/Code/get-skills/uploads"
    if os.path.exists(uploads_dir):
        pdf_files = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
        test_files.extend(pdf_files[:1])  # Add one PDF file for testing
    
    success_count = 0
    total_tests = len(test_files)
    
    for file_path in test_files:
        if test_file_upload(file_path, server_url):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 55)
    print(f"🎯 Test Results: {success_count}/{total_tests} files uploaded successfully")
    
    if success_count > 0:
        print(f"\n🎉 Success! Your application is working correctly!")
        print(f"🌐 Open your browser to: {server_url}")
        print("\n📝 What you can test in the browser:")
        print("   • Upload PDF files (.pdf)")
        print("   • Upload Excel files (.xlsx, .xls)")
        print("   • View extracted skills")
        print("   • Check document history")
        print("   • View skills statistics")
    else:
        print(f"\n❌ No files were uploaded successfully. Check the errors above.")

if __name__ == "__main__":
    main()
