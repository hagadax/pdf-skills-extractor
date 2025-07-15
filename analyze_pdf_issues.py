#!/usr/bin/env python3
"""
Advanced PDF analysis to understand extraction issues
"""

import PyPDF2
import os

def analyze_pdf_properties(filepath):
    """Analyze PDF properties and metadata"""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"📄 PDF Analysis for: {filepath}")
            print("=" * 60)
            
            # Basic info
            print(f"Pages: {len(pdf_reader.pages)}")
            
            # Metadata
            if pdf_reader.metadata:
                print("\n📋 Metadata:")
                for key, value in pdf_reader.metadata.items():
                    print(f"  {key}: {value}")
            
            # Check first page in detail
            if len(pdf_reader.pages) > 0:
                first_page = pdf_reader.pages[0]
                print(f"\n📄 First Page Analysis:")
                
                # Try different extraction methods
                print("\n🔍 Standard extraction (first 500 chars):")
                standard_text = first_page.extract_text()
                print(f"'{standard_text[:500]}...'")
                
                # Check if page has fonts
                if '/Font' in first_page.get('/Resources', {}):
                    print(f"\n🔤 Fonts detected: {len(first_page['/Resources']['/Font'])}")
                    for font_name, font_obj in first_page['/Resources']['/Font'].items():
                        print(f"  - {font_name}: {font_obj.get('/BaseFont', 'Unknown')}")
                
                # Check encoding issues
                print(f"\n📊 Text Statistics:")
                print(f"  - Length: {len(standard_text)}")
                print(f"  - Character set sample: {set(list(standard_text[:100]))}")
                
                # Look for Norwegian characters
                norwegian_chars = set('æøåÆØÅ')
                found_norwegian = norwegian_chars.intersection(set(standard_text))
                if found_norwegian:
                    print(f"  - Norwegian characters found: {found_norwegian}")
                else:
                    print("  - No Norwegian characters detected (encoding issue?)")
                    
    except Exception as e:
        print(f"Error analyzing PDF: {e}")

def test_alternative_extraction():
    """Test if we can extract readable text"""
    filepath = "uploads/Senior_backend-utvikler_-_arbeidsplassen.no.pdf"
    
    print("\n" + "=" * 60)
    print("🔧 ALTERNATIVE EXTRACTION METHODS")
    print("=" * 60)
    
    # Try basic method first
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Method 1: Raw extraction without cleaning
            print("\n1️⃣ Raw extraction (no cleaning):")
            raw_text = ""
            for page in pdf_reader.pages:
                raw_text += page.extract_text()
            print(f"First 300 chars: '{raw_text[:300]}'")
            
            # Method 2: Try different encodings in output
            print("\n2️⃣ Character analysis:")
            char_counts = {}
            for char in raw_text[:1000]:
                char_counts[char] = char_counts.get(char, 0) + 1
            
            # Show most common characters
            sorted_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)
            print("Most common characters:", sorted_chars[:20])
            
            # Method 3: Look for skill-like patterns even in corrupted text
            print("\n3️⃣ Pattern matching in corrupted text:")
            potential_skills = []
            
            # Look for common programming patterns
            programming_patterns = [
                r'jv',        # Java corrupted
                r'pyhon',     # Python corrupted  
                r'jscrp',     # JavaScript corrupted
                r'rek',       # React corrupted
                r'sprig',     # Spring corrupted
                r'pos',       # Postgres corrupted
                r'mysq',      # MySQL corrupted
                r'dokr',      # Docker corrupted
            ]
            
            import re
            text_lower = raw_text.lower()
            for pattern in programming_patterns:
                if re.search(pattern, text_lower):
                    potential_skills.append(pattern)
            
            if potential_skills:
                print(f"Potential corrupted skills found: {potential_skills}")
            else:
                print("No recognizable skill patterns found")
                
    except Exception as e:
        print(f"Error in alternative extraction: {e}")

if __name__ == "__main__":
    filepath = "uploads/Senior_backend-utvikler_-_arbeidsplassen.no.pdf"
    if os.path.exists(filepath):
        analyze_pdf_properties(filepath)
        test_alternative_extraction()
    else:
        print(f"File not found: {filepath}")
