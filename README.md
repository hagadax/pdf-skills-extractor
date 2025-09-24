# PDF Skills Extractor

A Flask web application that extracts technology skills from PDF documents and tracks their occurrence counts.

## Features

- 📄 Upload PDF documents (up to 16MB)
- 🔍 Extract technology skills from PDF text
- 🎯 Unique skill extraction (each skill counted once per document)
- 📊 Track skill occurrence counts
- 📈 View statistics and top skills
- 📉 Interactive cumulative growth chart for top 10 skills
- 🌐 REST API endpoint for programmatic access
- 🎨 Modern, responsive web interface
- 🔍 Search functionality for skills
- 📋 Skills with document references and file dates
- 📁 Document library with metadata and skills

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Upload PDF documents using the web interface

4. View extracted skills and statistics

## API Endpoints

- `GET /` - Main page with upload form and statistics
- `POST /upload` - Upload PDF file for skill extraction
- `GET /skills` - View all extracted skills
- `GET /ai-skills` - View AI-extracted skills
- `GET /documents` - View all processed documents with metadata
- `GET /comparison` - Compare pattern matching vs AI extraction results
- `GET /monthly-dashboard` - Monthly analysis and reports
- `GET /about` - About page with application information and purpose
- `GET /api/skills` - JSON API endpoint with skill data
- `GET /reset` - Reset all skill statistics

## Supported Skills

The application recognizes over 100 technology skills including:

- **Programming Languages**: Python, JavaScript, Java, C++, Ruby, Go, etc.
- **Web Technologies**: React, Angular, Vue.js, Node.js, Django, Flask, etc.
- **Databases**: MySQL, PostgreSQL, MongoDB, Redis, etc.
- **Cloud Platforms**: AWS, Azure, Google Cloud, etc.
- **DevOps Tools**: Docker, Kubernetes, Jenkins, Git, etc.
- **Mobile Development**: React Native, Flutter, Swift, Kotlin, etc.
- **Data Science**: TensorFlow, PyTorch, Pandas, NumPy, etc.
- **And many more...**

## File Structure

```
get-skills/
├── app.py              # Main Flask application
├── skills.py           # List of technology skills
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── index.html     # Main page template
│   ├── skills.html    # Skills listing page
│   ├── ai_skills.html # AI skills page
│   ├── documents.html # Document library page
│   ├── comparison.html # Comparison page template
│   ├── monthly_dashboard.html # Monthly analysis template
│   └── about.html     # About page with app information
└── uploads/           # Directory for uploaded PDFs (created automatically)
```

## How It Works

1. **PDF Upload**: Users upload PDF documents through the web interface
2. **Text Extraction**: PyPDF2 extracts text content from the PDF
3. **Date Extraction**: PDF creation date is extracted from metadata when available
4. **Skill Detection**: The application uses regex pattern matching to identify technology skills
5. **Unique Extraction**: Each skill is counted only once per document, regardless of frequency
6. **Count Tracking**: Each detected unique skill increments a global counter
7. **Monthly Tracking**: Skills are tracked by month for cumulative growth analysis
7. **Document Tracking**: Skills are linked to source documents with dates
8. **Statistics Display**: The web interface shows top skills, overall statistics, and cumulative growth charts

## Customization

You can customize the list of recognized skills by editing the `tech_skills` list in `skills.py`.

## Security Notes

- Files are saved with secure filenames using `werkzeug.utils.secure_filename`
- File size is limited to 16MB
- Only PDF files are accepted
- Secret key should be changed in production

## License

This project is open source and available under the MIT License.
