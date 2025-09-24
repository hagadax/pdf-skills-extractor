#!/usr/bin/env python3
"""
Test multilingual AI extraction capabilities for Norwegian and English content.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_skills import AISkillExtractor

def test_multilingual_extraction():
    """Test AI extraction with Norwegian and English content."""
    
    # Initialize AI extractor
    extractor = AISkillExtractor()
    
    if not extractor.client:
        print("❌ AI client not configured. Please check your Azure OpenAI or OpenAI configuration.")
        return
    
    print(f"✅ AI Service: {extractor.service_type}")
    print(f"✅ Model: {extractor.model_name}")
    print("-" * 60)
    
    # Test cases with multilingual content
    test_cases = [
        {
            "name": "Pure Norwegian Resume",
            "text": """
            CV - Senior Backend Utvikler
            
            Erfaring:
            • 5 års erfaring med Java og Spring Boot utvikling
            • Ekspert på REST API design og implementasjon
            • Jobbet med Docker og Kubernetes i produksjonsettinger
            • Utviklet mikrotjenester med PostgreSQL og Redis
            • Kjennskap til Agile metodikk og Scrum prosesser
            
            Tekniske ferdigheter:
            • Programmeringsspråk: Java, Python, JavaScript
            • Rammeverk: Spring Boot, React, Node.js
            • Databaser: PostgreSQL, MongoDB, Redis
            • DevOps: Docker, Kubernetes, Jenkins, Git
            • Skyplattformer: Azure, AWS
            
            Personlige egenskaper:
            • Sterk kommunikasjonsevne
            • Problemløsning og analytisk tenkning
            • Teamsamarbeid og lederskap
            • Fleksibilitet og tilpasningsevne
            """,
            "type": "resume"
        },
        {
            "name": "Norwegian Job Description",
            "text": """
            Stillingstittel: Senior Backend-utvikler
            
            Vi søker en erfaren backend-utvikler til vårt team i Oslo.
            
            Ansvarsområder:
            • Utvikle og vedlikeholde Java-baserte applikasjoner
            • Designe og implementere REST APIer
            • Arbeide med microservices arkitektur
            • Samarbeide med frontend-team og designere
            • Delta i code reviews og tekniske diskusjoner
            
            Krav:
            • Minimum 3 års erfaring med Java utvikling
            • God kjennskap til Spring Framework og Spring Boot
            • Erfaring med Docker og containerisering
            • Kjennskap til PostgreSQL eller lignende databaser
            • Erfaring med Git og CI/CD pipelines
            • Gode norskferdigheter i tale og skrift
            
            Ønskelige kvalifikasjoner:
            • Erfaring med Kubernetes og sky-plattformer (Azure/AWS)
            • Kjennskap til React eller andre frontend-teknologier
            • Erfaring med Agile/Scrum metodikk
            • Sertifiseringer innen cloud computing
            """,
            "type": "job_description"
        },
        {
            "name": "Mixed English-Norwegian",
            "text": """
            Senior Full-Stack Developer Position i Oslo
            
            We are looking for a senior full-stack utvikler with experience i both 
            frontend og backend teknologier.
            
            Required skills:
            • Python med Django eller Flask
            • JavaScript og moderne frameworks som React eller Vue.js
            • Database erfaring: PostgreSQL, MongoDB
            • Cloud platforms: AWS eller Azure
            • DevOps tools: Docker, Kubernetes, Jenkins
            • Version control: Git og GitHub/GitLab
            
            Personlige egenskaper:
            • Excellent communication skills på både engelsk og norsk
            • Strong problem-solving abilities
            • Team collaboration og leadership potential
            • Continuous learning mindset
            
            Vi tilbyr:
            • Competitive lønn og benefits package
            • Flexible working hours og remote work options
            • Professional development opportunities
            • Modern tech stack og innovative projects
            """,
            "type": "job_description"
        },
        {
            "name": "Technical Norwegian Description",
            "text": """
            Teknisk Arkitekt - Cloud og Infrastruktur
            
            Arbeidsoppgaver:
            • Planlegge og implementere skalerbare cloud-løsninger på Azure
            • Designe mikrotjenestearkitekturer med Docker og Kubernetes
            • Etablere CI/CD-pipelines med Azure DevOps og GitHub Actions
            • Jobbe med infrastruktur som kode (Terraform, ARM templates)
            • Sikkerhetshåndtering og compliance i cloud-miljøer
            
            Tekniske kompetanser:
            • Azure (AKS, App Service, Service Bus, Application Insights)
            • Containerteknologi: Docker, Kubernetes, OpenShift
            • Programmeringsspråk: C#, Python, PowerShell
            • Databases: SQL Server, CosmosDB, Redis Cache
            • Overvåking: Prometheus, Grafana, ELK Stack
            • Sikkerhet: Azure AD, Key Vault, SSL/TLS
            
            Metodikk og prosesser:
            • Agile utvikling og DevOps-prinsipper
            • Test-driven development (TDD)
            • Continuous Integration/Continuous Deployment
            • Infrastructure as Code (IaC)
            • Site Reliability Engineering (SRE)
            """,
            "type": "job_description"
        }
    ]
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        skills, metadata = extractor.extract_skills_from_text(
            test_case['text'], 
            test_case['type']
        )
        
        if skills:
            print(f"✅ Extracted {len(skills)} skills:")
            
            # Categorize skills
            technical_skills = []
            soft_skills = []
            
            # Simple categorization based on common patterns
            soft_skill_keywords = [
                'communication', 'leadership', 'teamwork', 'problem solving',
                'analytical', 'creative', 'adaptability', 'flexibility',
                'collaboration', 'interpersonal', 'presentation', 'negotiation',
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
                print("   📱 Technical Skills:")
                for skill in sorted(technical_skills):
                    print(f"      • {skill}")
            
            if soft_skills:
                print("   🧠 Soft Skills:")
                for skill in sorted(soft_skills):
                    print(f"      • {skill}")
            
            print(f"   🔧 Extraction Method: {metadata.get('ai_service', 'Unknown')}")
            print(f"   🤖 Model: {metadata.get('model', 'Unknown')}")
            
        else:
            print("❌ No skills extracted")
        
        print()

if __name__ == "__main__":
    test_multilingual_extraction()