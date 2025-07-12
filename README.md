# 🔍 Job Portal with AI-Powered CV Matching

A microservices-based job portal using Django and Celery that matches job seekers to jobs using AI.

## ⚙️ Tech Stack

- **Django** + **DRF** for APIs  
- **Celery** + **Redis** for async tasks  
- **FAISS** + **Sentence Transformers** for CV/job matching  
- **PostgreSQL** as the database  


## 📦 Features

- Users upload CVs (PDF)
- Employers post jobs
- Users can apply for the jobs
- AI matches CVs and jobs
- Top 5 matches stored
- Periodic cleanup of expired job matches
- Triggers run on new CV or job post

