from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import os
import re
import PyPDF2
from werkzeug.utils import secure_filename
from collections import defaultdict, Counter
from datetime import datetime
import io
import tempfile
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from skills import tech_skills
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# Azure Blob Storage configuration
AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER_NAME = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'uploads')

# Initialize Azure Blob Service Client with Managed Identity
def get_blob_service_client():
    """Initialize Azure Blob Service Client using Managed Identity or connection string."""
    try:
        if AZURE_STORAGE_CONNECTION_STRING:
            return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        else:
            # Use Managed Identity for authentication
            credential = DefaultAzureCredential()
            account_url = f"https://{os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')}.blob.core.windows.net"
            return BlobServiceClient(account_url=account_url, credential=credential)
    except Exception as e:
        print(f"Error initializing blob service client: {e}")
        return None

# Ensure upload directory exists (fallback for local development)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global skill tracker
skill_counter = Counter()

# Track skills by document with metadata
# Structure: {skill: [{filename, upload_date, file_date}, ...]}
skill_documents = defaultdict(list)

# Track all processed documents
# Structure: {filename: {upload_date, file_date, skills_found}}
processed_documents = {}

# Track monthly skill data for charts
# Structure: {skill: {'2025-01': 5, '2025-02': 3, ...}}
monthly_skill_data = defaultdict(lambda: defaultdict(int))

# Stats persistence configuration
STATS_BLOB_NAME = 'app_stats.json'
STATS_CONTAINER_NAME = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'uploads')

def save_stats_to_blob():
    """Save application statistics to Azure Blob Storage as JSON."""
    try:
        blob_service_client = get_blob_service_client()
        if not blob_service_client:
            print("Warning: Azure Blob Storage not available for stats persistence")
            return False
        
        # Prepare stats data for serialization
        stats_data = {
            'skill_counter': dict(skill_counter),
            'skill_documents': dict(skill_documents),
            'processed_documents': processed_documents,
            'monthly_skill_data': {
                skill: dict(months) for skill, months in monthly_skill_data.items()
            },
            'last_updated': datetime.now().isoformat()
        }
        
        # Convert to JSON
        stats_json = json.dumps(stats_data, indent=2, default=str)
        
        # Upload to blob storage
        blob_client = blob_service_client.get_blob_client(
            container=STATS_CONTAINER_NAME,
            blob=STATS_BLOB_NAME
        )
        
        blob_client.upload_blob(stats_json, overwrite=True)
        print("Stats saved to blob storage successfully")
        return True
        
    except Exception as e:
        print(f"Error saving stats to blob storage: {e}")
        return False

def load_stats_from_blob():
    """Load application statistics from Azure Blob Storage."""
    try:
        blob_service_client = get_blob_service_client()
        if not blob_service_client:
            print("Info: Azure Blob Storage not available, starting with empty stats")
            return False
        
        blob_client = blob_service_client.get_blob_client(
            container=STATS_CONTAINER_NAME,
            blob=STATS_BLOB_NAME
        )
        
        # Check if stats file exists
        if not blob_client.exists():
            print("Info: No existing stats found, starting with empty stats")
            return False
        
        # Download and parse stats
        stats_content = blob_client.download_blob().readall()
        stats_data = json.loads(stats_content.decode('utf-8'))
        
        # Restore global variables
        global skill_counter, skill_documents, processed_documents, monthly_skill_data
        
        skill_counter = Counter(stats_data.get('skill_counter', {}))
        
        # Restore skill_documents (convert back to defaultdict)
        skill_documents_data = stats_data.get('skill_documents', {})
        skill_documents = defaultdict(list)
        for skill, docs in skill_documents_data.items():
            skill_documents[skill] = docs
        
        processed_documents = stats_data.get('processed_documents', {})
        
        # Restore monthly_skill_data (convert back to nested defaultdict)
        monthly_data = stats_data.get('monthly_skill_data', {})
        monthly_skill_data = defaultdict(lambda: defaultdict(int))
        for skill, months in monthly_data.items():
            monthly_skill_data[skill] = defaultdict(int, months)
        
        last_updated = stats_data.get('last_updated', 'Unknown')
        print(f"Stats loaded from blob storage successfully (last updated: {last_updated})")
        return True
        
    except Exception as e:
        print(f"Error loading stats from blob storage: {e}")
        return False

# Load stats on application startup
try:
    load_stats_from_blob()
except Exception as e:
    print(f"Failed to load stats on startup: {e}")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_content):
    """Extract text content from a PDF file (from bytes or file path)."""
    try:
        if isinstance(file_content, str):
            # Legacy support for file paths
            with open(file_content, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
        else:
            # Handle bytes content from blob storage
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        
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

def get_pdf_creation_date(file_content):
    """Extract creation date from PDF metadata (from bytes or file path)."""
    try:
        if isinstance(file_content, str):
            # Legacy support for file paths
            with open(file_content, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
        else:
            # Handle bytes content from blob storage
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        
        if pdf_reader.metadata and '/CreationDate' in pdf_reader.metadata:
            creation_date = pdf_reader.metadata.get('/CreationDate')
            if creation_date:
                # PDF dates are in format D:YYYYMMDDHHmmSSOHH'mm
                date_str = str(creation_date)
                if date_str.startswith('D:'):
                    date_str = date_str[2:16]  # Extract YYYYMMDDHHMMSS
                    try:
                        return datetime.strptime(date_str[:8], '%Y%m%d').strftime('%Y-%m-%d')
                    except:
                        pass
        return None
    except Exception as e:
        print(f"Error extracting PDF date: {e}")
        return None

def extract_skills(text):
    """Extract technology skills from text using improved pattern matching.
    Handles PDF text fragmentation and skill variations."""
    found_skills = set()  # Use set to ensure uniqueness
    
    # Normalize text: remove excessive whitespace and line breaks
    normalized_text = ' '.join(text.split()).lower()
    
    # Also create a version without spaces for compound skills
    no_spaces_text = re.sub(r'\s+', '', text.lower())
    
    for skill in tech_skills:
        skill_lower = skill.lower()
        skill_found = False
        
        # Method 1: Standard word boundary matching (for simple skills)
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, normalized_text):
            skill_found = True
        
        # Method 2: Flexible matching for compound skills (allows spaces/dots)
        # Handle skills like "Node.js", "Vue.js", "C++", "C#", etc.
        flexible_pattern = re.escape(skill_lower)
        flexible_pattern = flexible_pattern.replace(r'\.', r'[\.\s]*')  # . or spaces
        flexible_pattern = flexible_pattern.replace(r'\+', r'[\+\s]*')  # + or spaces  
        flexible_pattern = flexible_pattern.replace(r'\#', r'[\#\s]*')  # # or spaces
        flexible_pattern = flexible_pattern.replace(r'\s', r'\s*')      # flexible spaces
        
        if re.search(r'\b' + flexible_pattern + r'\b', normalized_text):
            skill_found = True
        
        # Method 3: No-spaces matching for fragmented text
        skill_no_spaces = re.sub(r'[\s\.\+\#-]', '', skill_lower)
        if len(skill_no_spaces) > 2 and skill_no_spaces in no_spaces_text:
            skill_found = True
        
        if skill_found:
            found_skills.add(skill)
    
    # Additional skill variations and aliases
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
    
    # Check for aliases in normalized text
    for alias, skill_name in skill_aliases.items():
        # Only add if the main skill wasn't already found
        if skill_name not in found_skills:
            alias_pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(alias_pattern, normalized_text):
                found_skills.add(skill_name)
    
    return list(found_skills)  # Convert back to list for consistency

def get_monthly_chart_data():
    """Generate chart data for top 10 skills over the past 12 months."""
    from datetime import datetime, timedelta
    import calendar
    
    # Get current date and calculate 12 months back
    current_date = datetime.now()
    months = []
    
    # Generate list of last 12 months in YYYY-MM format
    for i in range(11, -1, -1):
        date = current_date - timedelta(days=i*30)  # Approximate month calculation
        month_key = date.strftime('%Y-%m')
        month_label = date.strftime('%b %Y')
        months.append({'key': month_key, 'label': month_label})
    
    # Get top 10 skills
    top_skills = [skill for skill, count in skill_counter.most_common(10)]
    
    # Prepare chart data
    chart_data = {
        'labels': [month['label'] for month in months],
        'datasets': []
    }
    
    # Color palette for the chart
    colors = [
        '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', 
        '#43e97b', '#fa709a', '#fee140', '#a8edea', '#d299c2'
    ]
    
    # Create dataset for each top skill
    for i, skill in enumerate(top_skills):
        skill_data = []
        cumulative_count = 0
        
        for month in months:
            # Add monthly occurrences to cumulative count
            monthly_occurrences = monthly_skill_data[skill].get(month['key'], 0)
            cumulative_count += monthly_occurrences
            skill_data.append(cumulative_count)
        
        # Only include skills that have data
        if cumulative_count > 0:
            chart_data['datasets'].append({
                'label': skill,
                'data': skill_data,
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)] + '20',  # 20 for transparency
                'tension': 0.4,
                'fill': False
            })
    
    return chart_data

@app.route('/')
def index():
    """Main page with upload form and skill statistics."""
    # Get top 10 most common skills
    top_skills = skill_counter.most_common(10)
    total_documents = len(processed_documents)
    
    # Get chart data for visualization
    chart_data = get_monthly_chart_data()
    
    return render_template('index.html', 
                         top_skills=top_skills, 
                         total_documents=total_documents,
                         total_skills=len(skill_counter),
                         chart_data=chart_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload and skill extraction."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        try:
            # Save file to Azure Blob Storage or local storage
            file_content, is_blob = save_file_safely(file, filename)
            
            # Get upload date and file creation date
            upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file_date = get_pdf_creation_date(file_content)
            
            # Extract text from PDF
            text = extract_text_from_pdf(file_content)
            
            if text:
                # Extract skills from text (each skill only counted once per document)
                found_skills = extract_skills(text)
                
                # Get month key for tracking (use file date if available, otherwise upload date)
                date_for_tracking = file_date if file_date else upload_date.split(' ')[0]
                month_key = date_for_tracking[:7]  # Get YYYY-MM format
                
                # Update global skill counter (each unique skill from this document)
                for skill in found_skills:
                    skill_counter[skill] += 1  # +1 per document, regardless of skill frequency in text
                    
                    # Track monthly data
                    monthly_skill_data[skill][month_key] += 1
                    
                    # Track which document contains this skill
                    skill_documents[skill].append({
                        'filename': filename,
                        'upload_date': upload_date,
                        'file_date': file_date or upload_date.split(' ')[0]  # Use upload date if no file date
                    })
                
                # Track processed document
                processed_documents[filename] = {
                    'upload_date': upload_date,
                    'file_date': file_date or upload_date.split(' ')[0],
                    'skills_found': found_skills,
                    'storage_type': 'blob' if is_blob else 'local'
                }
                
                # Save stats to blob storage after processing
                save_stats_to_blob()
                
                storage_msg = 'Azure Blob Storage' if is_blob else 'local storage'
                return jsonify({
                    'success': True, 
                    'message': f'Successfully processed {filename} (saved to {storage_msg}). Found {len(found_skills)} skills: {", ".join(found_skills)}',
                    'skills': found_skills,
                    'filename': filename
                })
            else:
                return jsonify({'success': False, 'message': f'Could not extract text from {filename}'})
                
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'})
    else:
        return jsonify({'success': False, 'message': 'Please upload a PDF file'})

@app.route('/api/skills')
def api_skills():
    """API endpoint to get skill statistics as JSON."""
    return jsonify({
        'total_skills': len(skill_counter),
        'skills': dict(skill_counter),
        'top_skills': skill_counter.most_common(20)
    })

@app.route('/skills')
def skills_page():
    """Page showing all skill statistics."""
    all_skills = skill_counter.most_common()
    return render_template('skills.html', skills=all_skills)

@app.route('/skill-details')
def skill_details():
    """Page showing skills with document references."""
    # Create a comprehensive view of skills with their documents
    skills_with_docs = []
    
    for skill, count in skill_counter.most_common():
        documents = skill_documents.get(skill, [])
        skills_with_docs.append({
            'skill': skill,
            'count': count,
            'documents': documents
        })
    
    return render_template('skill_details.html', skills_data=skills_with_docs)

@app.route('/documents')
def documents_page():
    """Page showing all processed documents."""
    return render_template('documents.html', documents=processed_documents)

@app.route('/about')
def about_page():
    """About page with application information."""
    # Calculate dynamic statistics
    total_skills_in_db = len(tech_skills)
    unique_skills_found = len(skill_counter)
    total_documents = len(processed_documents)
    total_skill_occurrences = sum(skill_counter.values())
    
    # Calculate categories (this is an approximation based on the skills.py structure)
    categories = [
        "Programming Languages", "Web Technologies", "Databases", "Cloud Platforms",
        "DevOps & Tools", "Mobile Development", "Data Science & AI", "Testing",
        "Operating Systems", "Version Control", "IDEs & Editors", "Methodologies",
        "Other Technologies"
    ]
    total_categories = len(categories)
    
    return render_template('about.html', 
                         total_skills_in_db=total_skills_in_db,
                         unique_skills_found=unique_skills_found,
                         total_documents=total_documents,
                         total_skill_occurrences=total_skill_occurrences,
                         total_categories=total_categories)

# Azure Blob Storage helper functions
# Stats persistence functions
def save_stats_to_blob():
    """Save all statistics to Azure Blob Storage as JSON files."""
    try:
        blob_service_client = get_blob_service_client()
        if not blob_service_client:
            return False
        
        stats_data = {
            'skill_counter': dict(skill_counter),
            'skill_documents': dict(skill_documents),
            'processed_documents': dict(processed_documents),
            'monthly_skill_data': {k: dict(v) for k, v in monthly_skill_data.items()},
            'last_updated': datetime.now().isoformat()
        }
        
        # Upload stats as JSON
        blob_client = blob_service_client.get_blob_client(
            container=AZURE_STORAGE_CONTAINER_NAME,
            blob='stats/app_statistics.json'
        )
        
        blob_client.upload_blob(
            json.dumps(stats_data, indent=2).encode('utf-8'),
            overwrite=True
        )
        return True
    except Exception as e:
        print(f"Error saving stats to blob: {e}")
        return False

def load_stats_from_blob():
    """Load statistics from Azure Blob Storage JSON files."""
    try:
        blob_service_client = get_blob_service_client()
        if not blob_service_client:
            return False
        
        blob_client = blob_service_client.get_blob_client(
            container=AZURE_STORAGE_CONTAINER_NAME,
            blob='stats/app_statistics.json'
        )
        
        stats_json = blob_client.download_blob().readall().decode('utf-8')
        stats_data = json.loads(stats_json)
        
        # Restore global variables
        global skill_counter, skill_documents, processed_documents, monthly_skill_data
        
        skill_counter = Counter(stats_data.get('skill_counter', {}))
        skill_documents = defaultdict(list, stats_data.get('skill_documents', {}))
        processed_documents = stats_data.get('processed_documents', {})
        monthly_skill_data = defaultdict(lambda: defaultdict(int))
        
        # Restore monthly data structure
        for skill, months in stats_data.get('monthly_skill_data', {}).items():
            for month, count in months.items():
                monthly_skill_data[skill][month] = count
        
        print(f"Stats loaded successfully. Last updated: {stats_data.get('last_updated', 'Unknown')}")
        return True
    except Exception as e:
        print(f"Error loading stats from blob: {e}")
        return False

# Load stats on application startup
if __name__ != '__main__':  # Only load when running in production
    load_stats_from_blob()

def upload_file_to_blob(file_content, filename):
    """Upload file to Azure Blob Storage."""
    try:
        blob_service_client = get_blob_service_client()
        if not blob_service_client:
            return False, "Azure Blob Storage not configured"
        
        blob_client = blob_service_client.get_blob_client(
            container=AZURE_STORAGE_CONTAINER_NAME,
            blob=filename
        )
        
        blob_client.upload_blob(file_content, overwrite=True)
        return True, "File uploaded successfully"
    except Exception as e:
        print(f"Error uploading to blob storage: {e}")
        return False, f"Upload failed: {str(e)}"

def download_file_from_blob(filename):
    """Download file from Azure Blob Storage."""
    try:
        blob_service_client = get_blob_service_client()
        if not blob_service_client:
            return None
        
        blob_client = blob_service_client.get_blob_client(
            container=AZURE_STORAGE_CONTAINER_NAME,
            blob=filename
        )
        
        return blob_client.download_blob().readall()
    except Exception as e:
        print(f"Error downloading from blob storage: {e}")
        return None

def save_file_safely(file, filename):
    """Save file to Azure Blob Storage or local storage (fallback)."""
    file_content = file.read()
    
    # Try Azure Blob Storage first
    blob_service_client = get_blob_service_client()
    if blob_service_client:
        success, message = upload_file_to_blob(file_content, filename)
        if success:
            return file_content, True  # Return content and success flag
    
    # Fallback to local storage
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'wb') as f:
        f.write(file_content)
    
    return file_content, False  # Return content and blob flag (False = local)

def get_file_content(filename, is_blob=True):
    """Get file content from Azure Blob Storage or local storage."""
    if is_blob:
        content = download_file_from_blob(filename)
        if content:
            return content
    
    # Fallback to local storage
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(filepath, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading local file: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)
