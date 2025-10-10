import os
import re
import csv
import docx2txt
import PyPDF2

# -------------------------------
# PATH SETUP
# -------------------------------

# Project root (one level above 'backend')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Job description file
JOB_DESC_FILE = os.path.join(BASE_DIR, "job_descriptions", "sample_job.txt")

# Folder containing resumes
RESUME_FOLDER = os.path.join(BASE_DIR, "resumes")

# Outputs folder
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Debug prints
print("BASE_DIR =", BASE_DIR)
print("JOB_DESC_FILE =", JOB_DESC_FILE)
print("RESUME_FOLDER =", RESUME_FOLDER)
print("Exists?", os.path.exists(JOB_DESC_FILE))

# -------------------------------
# JOB DESCRIPTION EXTRACTION
# -------------------------------
with open(JOB_DESC_FILE, 'r', encoding='utf-8') as f:
    job_text = f.read().lower()

# Define skills to match
SKILL_KEYWORDS = [
    "python", "java", "c++", "sql", "javascript",
    "machine learning", "deep learning", "data analysis",
    "html", "css", "react", "node.js",
    "cloud computing", "aws", "azure", "docker", "kubernetes"
]

# Optional course recommendations
COURSE_RECOMMENDATIONS = {
    "python": "Python Programming Course",
    "java": "Java Programming Course",
    "c++": "C++ Fundamentals",
    "sql": "SQL Fundamentals",
    "javascript": "JavaScript Essentials",
    "machine learning": "Intro to Machine Learning",
    "deep learning": "Deep Learning Specialization",
    "data analysis": "Data Analysis with Python",
    "html": "HTML & CSS Basics",
    "css": "HTML & CSS Basics",
    "react": "React Essentials",
    "node.js": "Node.js Fundamentals",
    "cloud computing": "Cloud Computing Basics",
    "aws": "AWS Certified Solutions Architect",
    "azure": "Azure Fundamentals",
    "docker": "Docker for Beginners",
    "kubernetes": "Kubernetes Basics"
}

# -------------------------------
# RESUME TEXT EXTRACTION FUNCTIONS
# -------------------------------
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text.lower()

def extract_text_from_docx(file_path):
    return docx2txt.process(file_path).lower()

# -------------------------------
# SKILL MATCHING
# -------------------------------
def extract_skills(resume_text):
    matched = [skill for skill in SKILL_KEYWORDS if skill.lower() in resume_text]
    missing = [skill for skill in SKILL_KEYWORDS if skill.lower() not in resume_text]
    match_percentage = round(len(matched) / len(SKILL_KEYWORDS) * 100, 2)
    return matched, missing, match_percentage

# -------------------------------
# MAIN PROCESS
# -------------------------------
if __name__ == "__main__":
    print("Job Required Skills:", SKILL_KEYWORDS)

    results = []

    for file_name in os.listdir(RESUME_FOLDER):
        file_path = os.path.join(RESUME_FOLDER, file_name)

        if file_name.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        elif file_name.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        else:
            continue

        matched, missing, match = extract_skills(text)
        results.append({
            "Resume": file_name,
            "Match (%)": match,
            "Matched Skills": ", ".join(matched),
            "Missing Skills": ", ".join(missing),
            "Recommended Courses": ", ".join([COURSE_RECOMMENDATIONS.get(skill, "") for skill in missing])
        })

        print(f"{file_name} - Match: {match}% - Matched Skills: {', '.join(matched)} - Missing Skills: {', '.join(missing)}")

    # Save results to CSV
    csv_file = os.path.join(OUTPUTS_DIR, "resume_match_results.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Resume", "Match (%)", "Matched Skills", "Missing Skills", "Recommended Courses"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to {csv_file}")
