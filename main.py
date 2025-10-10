from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from .resume_skill_matcher import extract_text_from_pdf, extract_text_from_docx, extract_skills, SKILL_KEYWORDS, COURSE_RECOMMENDATIONS

app = FastAPI()

# Enable CORS for React frontend
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
JOB_DESC_FILE = "job_descriptions/sample_job.txt"

# Load Job Skills
with open(JOB_DESC_FILE, 'r', encoding='utf-8') as f:
    job_text = f.read().lower()
job_skills = extract_skills(job_text)
job_skills_lower = [s.lower() for s in job_skills]

SOFT_SKILLS = ["Communication", "Teamwork", "Leadership", "Problem Solving", "Adaptability", "Creativity"]

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text
    if file.filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(file_path)
    else:
        resume_text = extract_text_from_docx(file_path)

    resume_text_clean = resume_text.lower()
    candidate_skills = extract_skills(resume_text_clean)
    candidate_skills_lower = [s.lower() for s in candidate_skills]

    matched_skills = list(set(candidate_skills_lower) & set(job_skills_lower))
    missing_skills = list(set(job_skills_lower) - set(candidate_skills_lower))
    match_percentage = (len(matched_skills)/len(job_skills))*100 if job_skills else 0
    candidate_soft = [s for s in SOFT_SKILLS if s.lower() in resume_text_clean]

    recommended_courses = []
    for skill in missing_skills:
        for key in SKILL_KEYWORDS:
            if key.lower() == skill and key in COURSE_RECOMMENDATIONS:
                recommended_courses.extend(COURSE_RECOMMENDATIONS[key])

    return {
        "resume": file.filename,
        "candidate_skills": candidate_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": match_percentage,
        "soft_skills": candidate_soft,
        "recommended_courses": recommended_courses
    }
