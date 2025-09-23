tech_skills = [
    # Programming Languages
    "Python", "JavaScript", "Java", "C++", "Ruby", "Go", "Swift", "Kotlin", 
    "PHP", "Rust", "TypeScript", "HTML", "CSS", "SQL", "R", "MATLAB", 
    "Bash", "Perl", "Scala", "Dart", "C#", "Objective-C", "Shell Scripting", 
    "PowerShell", "Haskell", "Elixir", "Clojure", "Lua", "Julia", "F#", 
    "Visual Basic", "Assembly Language", "Groovy", "Erlang", "COBOL", 
    "Fortran", "Ada", "Prolog", "C", "VB.NET",
    
    # Web Technologies
    "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django", 
    "Flask", "Laravel", "Spring Boot", "ASP.NET", "jQuery", "Bootstrap", 
    "Tailwind CSS", "SASS", "SCSS", "Webpack", "Vite", "Next.js", "Nuxt.js",
    "Svelte", "Ember.js", "Backbone.js", "Meteor", "Gatsby",
    
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "SQL Server", 
    "Redis", "Cassandra", "DynamoDB", "Firebase", "Neo4j", "CouchDB", 
    "MariaDB", "Elasticsearch", "InfluxDB", "Amazon RDS",
    
    # Cloud Platforms
    "AWS", "Azure", "Google Cloud", "GCP", "Heroku", "DigitalOcean", 
    "Vercel", "Netlify", "CloudFlare", "IBM Cloud", "Oracle Cloud",
    
    # DevOps & Tools
    "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab", 
    "Bitbucket", "CI/CD", "Terraform", "Ansible", "Chef", "Puppet", 
    "Vagrant", "CircleCI", "Travis CI", "GitHub Actions", "Bamboo",
    "Apache", "Nginx", "Tomcat", "IIS",
    
    # Mobile Development
    "React Native", "Flutter", "Xamarin", "Ionic", "Cordova", 
    "Android Development", "iOS Development", "Unity",
    
    # Data Science & AI
    "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", 
    "NumPy", "Matplotlib", "Seaborn", "Jupyter", "Apache Spark", 
    "Hadoop", "Tableau", "Power BI", "D3.js", "OpenCV", "NLTK", 
    "spaCy", "Plotly", "Bokeh",
    
    # Testing
    "Jest", "Mocha", "Chai", "Cypress", "Selenium", "JUnit", 
    "TestNG", "PyTest", "Postman", "Insomnia", "SoapUI",
    
    # Operating Systems
    "Linux", "Windows", "macOS", "Ubuntu", "CentOS", "Red Hat", 
    "Debian", "UNIX", "FreeBSD",
    
    # Version Control
    "Git", "SVN", "Mercurial", "Perforce",
    
    # IDEs & Editors
    "Visual Studio Code", "IntelliJ IDEA", "Eclipse", "Sublime Text", 
    "Atom", "Vim", "Emacs", "PyCharm", "WebStorm", "Xcode", 
    "Android Studio", "Visual Studio",
    
    # Methodologies
    "Agile", "Scrum", "Kanban", "DevOps", "TDD", "BDD", "Waterfall", 
    "Lean", "Six Sigma", "ITIL",
    
    # Other Technologies
    "REST API", "GraphQL", "SOAP", "Microservices", "Blockchain", 
    "Machine Learning", "Artificial Intelligence", "Internet of Things", 
    "IoT", "Augmented Reality", "AR", "Virtual Reality", "VR", 
    "Big Data", "Data Mining", "ETL", "API Development", "JSON", 
    "XML", "YAML", "OAuth", "JWT", "SSL", "HTTPS", "WebSockets",
    "gRPC", "Apache Kafka", "RabbitMQ", "Message Queues"
]

# Global skill tracking variables
from collections import Counter, defaultdict
skill_counter = Counter()
monthly_skill_data = defaultdict(lambda: defaultdict(int))
skill_documents = defaultdict(list)
processed_documents = {}

# Skills extraction function
import re

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
        
        # Method 4: Partial matching for longer skills (be more careful here)
        if len(skill_lower) > 4:
            # Split longer skills and check if major parts are present
            words = skill_lower.split()
            if len(words) > 1:
                # For multi-word skills, check if all words are present nearby
                all_words_found = True
                for word in words:
                    if len(word) > 2 and word not in normalized_text:
                        all_words_found = False
                        break
                if all_words_found:
                    skill_found = True
        
        if skill_found:
            found_skills.add(skill)
    
    return list(found_skills)

def categorize_skills(skills_list):
    """Categorize skills into technical and soft skills."""
    technical_skills = []
    soft_skills = []
    
    # Extended list of common soft skills
    soft_skill_keywords = [
        'communication', 'leadership', 'teamwork', 'problem solving', 
        'critical thinking', 'creativity', 'adaptability', 'time management',
        'project management', 'analytical', 'detail oriented', 'organized',
        'collaborative', 'innovative', 'strategic', 'mentoring', 'coaching',
        'presentation', 'negotiation', 'decision making', 'interpersonal',
        'customer service', 'conflict resolution', 'emotional intelligence',
        'multitasking', 'self motivated', 'proactive', 'reliable',
        'flexible', 'patient', 'empathetic', 'diplomatic', 'persuasive'
    ]
    
    for skill in skills_list:
        skill_lower = skill.lower()
        is_soft_skill = any(keyword in skill_lower for keyword in soft_skill_keywords)
        
        if is_soft_skill:
            soft_skills.append(skill)
        else:
            # Check if it's in our tech skills list
            if skill in tech_skills:
                technical_skills.append(skill)
            else:
                # If not clearly categorized, treat as technical by default
                technical_skills.append(skill)
    
    return {
        'technical': technical_skills,
        'soft': soft_skills
    }

def get_skill_statistics():
    """Get current skill statistics."""
    return {
        'total_skills': len(skill_counter),
        'total_extractions': sum(skill_counter.values()),
        'top_skills': skill_counter.most_common(10),
        'total_documents': len(processed_documents)
    }

def update_skill_tracking(document_name, skills):
    """Update skill tracking data."""
    global skill_counter, skill_documents, processed_documents
    from datetime import datetime
    
    # Update counters
    for skill in skills:
        skill_counter[skill] += 1
        skill_documents[skill].append(document_name)
    
    # Track document
    processed_documents[document_name] = {
        'skills': skills,
        'processed_at': datetime.now().isoformat(),
        'skill_count': len(skills)
    }
    
    # Update monthly data
    current_month = datetime.now().strftime('%Y-%m')
    for skill in skills:
        monthly_skill_data[current_month][skill] += 1

def get_monthly_skill_data():
    """Get monthly skill tracking data."""
    return dict(monthly_skill_data)