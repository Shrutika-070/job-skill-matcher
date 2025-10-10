import docx2txt
import PyPDF2
import re

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + " "
    return text.lower()

# Function to extract text from DOCX
def extract_text_from_docx(file):
    text = docx2txt.process(file)
    return text.lower()

# Function to extract skills from resume text
def extract_resume_skills(file):
    filename = file.name.lower()
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(file)
    else:
        text = ""
    # Simple skill matching using keywords
    skills_list = ["python", "java", "c++", "sql", "javascript", "machine learning",
                   "deep learning", "data analysis", "html", "css", "react",
                   "node.js", "cloud computing", "aws", "azure", "docker", "kubernetes"]
    skills_found = [skill for skill in skills_list if re.search(r"\b"+skill+r"\b", text)]
    return skills_found

# Function to extract skills from job description text
def get_job_skills(job_text):
    job_text = job_text.lower()
    skills_list = ["python", "java", "c++", "sql", "javascript", "machine learning",
                   "deep learning", "data analysis", "html", "css", "react",
                   "node.js", "cloud computing", "aws", "azure", "docker", "kubernetes"]
    required_skills = [skill for skill in skills_list if skill in job_text]
    return required_skills

# Main function for Streamlit to call
def match_resumes(job_text, resume_files):
    job_skills = get_job_skills(job_text)
    results = []

    for file in resume_files:
        resume_name = file.name
        skills = extract_resume_skills(file)
        matched_skills = [skill for skill in skills if skill in job_skills]
        missing_skills = [skill for skill in job_skills if skill not in skills]

        match_percent = round(len(matched_skills)/len(job_skills)*100, 2) if job_skills else 0

        results.append({
            'resume_name': resume_name,
            'match_percent': match_percent,
            'matched_skills': ", ".join(matched_skills),
            'missing_skills': ", ".join(missing_skills)
        })
    return results
