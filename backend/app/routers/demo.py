"""
Demo mode endpoints - provides sample data for users to try the app without API keys.
"""
from fastapi import APIRouter
from typing import List

router = APIRouter()


DEMO_RESUME = {
    "id": "demo-resume-1",
    "filename": "sample_resume.pdf",
    "parsed_data": {
        "name": "Alex Johnson",
        "email": "alex.johnson@email.com",
        "phone": "+1 (555) 123-4567",
        "location": "San Francisco, CA",
        "summary": "Full-stack software engineer with 5+ years of experience building scalable web applications. Passionate about clean code, user experience, and shipping products that matter.",
        "skills": [
            "Python", "JavaScript", "React", "Node.js", "FastAPI", "PostgreSQL",
            "Docker", "AWS", "CI/CD", "Git", "Agile", "REST APIs"
        ],
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "TechCorp Inc.",
                "location": "San Francisco, CA",
                "start_date": "2021-03",
                "end_date": "Present",
                "description": "Led development of microservices architecture serving 1M+ daily users. Built RESTful APIs with FastAPI and React frontends. Improved deployment pipeline reducing release time by 60%."
            },
            {
                "title": "Software Engineer",
                "company": "StartupXYZ",
                "location": "Remote",
                "start_date": "2019-01",
                "end_date": "2021-02",
                "description": "Developed full-stack features for SaaS platform using React, Node.js, and MongoDB. Collaborated with product team on feature prioritization. Mentored junior developers on best practices."
            },
            {
                "title": "Junior Developer",
                "company": "CodeAgency",
                "location": "Austin, TX",
                "start_date": "2017-06",
                "end_date": "2018-12",
                "description": "Built client websites with modern JavaScript frameworks. Worked closely with designers to implement pixel-perfect UIs. Maintained legacy PHP applications."
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "school": "University of California, Berkeley",
                "graduation_year": "2017"
            }
        ]
    },
    "created_at": "2026-05-01T10:00:00Z"
}


DEMO_JOBS = [
    {
        "id": "demo-job-1",
        "title": "Senior Full Stack Engineer",
        "company": "Stripe",
        "location": "San Francisco, CA",
        "description": "Join our Payments Platform team to build the infrastructure powering millions of businesses. We're looking for experienced engineers who love solving complex problems and building delightful user experiences. You'll work on React frontends, Python/Ruby backends, and distributed systems at scale.",
        "requirements": "5+ years of software engineering experience, strong proficiency in Python or Ruby, experience with React, deep understanding of web technologies, passion for developer tools.",
        "salary_min": 180000,
        "salary_max": 250000,
        "job_type": "Full-time",
        "remote": False,
        "apply_url": "https://stripe.com/jobs",
        "source": "demo",
        "match_score": 0.92,
        "match_reasons": [
            "Strong match on Python, React, and full-stack experience",
            "Your 5+ years aligns perfectly with requirements",
            "Relevant experience with APIs and scalable systems"
        ],
        "missing_skills": ["Ruby", "Stripe API knowledge"]
    },
    {
        "id": "demo-job-2",
        "title": "Backend Engineer - AI/ML Platform",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "description": "Help build the platform that powers ChatGPT and GPT-4. We need backend engineers to scale our infrastructure, optimize API performance, and ensure reliability for millions of users. FastAPI, Python, and PostgreSQL experience highly valued.",
        "requirements": "Strong Python skills, experience with FastAPI or similar frameworks, database optimization experience, familiarity with ML systems (bonus), excellent problem-solving skills.",
        "salary_min": 200000,
        "salary_max": 300000,
        "job_type": "Full-time",
        "remote": True,
        "apply_url": "https://openai.com/careers",
        "source": "demo",
        "match_score": 0.89,
        "match_reasons": [
            "Perfect match on Python and FastAPI experience",
            "PostgreSQL database skills align well",
            "Your API development background is highly relevant"
        ],
        "missing_skills": ["ML/AI frameworks", "LLM fine-tuning"]
    },
    {
        "id": "demo-job-3",
        "title": "React Engineer",
        "company": "Airbnb",
        "location": "Remote (US)",
        "description": "Join our Host Tools team to build interfaces that help millions of hosts manage their listings. We're looking for React specialists who care about performance, accessibility, and user experience. You'll work on a modern stack: React, TypeScript, GraphQL, and Node.js microservices.",
        "requirements": "3+ years React experience, TypeScript proficiency, strong CSS skills, experience with state management (Redux/MobX), passion for UI/UX, remote work experience.",
        "salary_min": 150000,
        "salary_max": 220000,
        "job_type": "Full-time",
        "remote": True,
        "apply_url": "https://careers.airbnb.com",
        "source": "demo",
        "match_score": 0.85,
        "match_reasons": [
            "Strong React experience matches well",
            "Your full-stack background includes relevant frontend work",
            "Remote work experience is a plus"
        ],
        "missing_skills": ["TypeScript", "GraphQL", "Redux"]
    },
    {
        "id": "demo-job-4",
        "title": "DevOps Engineer",
        "company": "GitHub",
        "location": "Remote (Worldwide)",
        "description": "Help us keep GitHub.com running smoothly for 100M+ developers. We need DevOps engineers to manage Kubernetes clusters, improve CI/CD pipelines, and build internal tooling. Docker, AWS, and automation scripting are must-haves.",
        "requirements": "Experience with Kubernetes, Docker, CI/CD (GitHub Actions preferred), AWS or GCP, scripting (Python/Bash), monitoring & observability tools, on-call rotation comfort.",
        "salary_min": 140000,
        "salary_max": 200000,
        "job_type": "Full-time",
        "remote": True,
        "apply_url": "https://github.com/about/careers",
        "source": "demo",
        "match_score": 0.78,
        "match_reasons": [
            "Docker and CI/CD experience mentioned in your resume",
            "AWS familiarity is relevant",
            "Your deployment pipeline work shows DevOps interest"
        ],
        "missing_skills": ["Kubernetes", "Terraform", "Prometheus"]
    },
    {
        "id": "demo-job-5",
        "title": "Full Stack JavaScript Developer",
        "company": "Notion",
        "location": "San Francisco, CA / New York, NY",
        "description": "Build the future of productivity tools. We're looking for full-stack engineers who love JavaScript/TypeScript across the entire stack. You'll work on Node.js backends, React frontends, and PostgreSQL databases to create delightful user experiences.",
        "requirements": "4+ years JavaScript/TypeScript experience, Node.js backend development, React proficiency, database design skills, passion for product quality, excellent communication.",
        "salary_min": 160000,
        "salary_max": 230000,
        "job_type": "Full-time",
        "remote": False,
        "apply_url": "https://notion.so/careers",
        "source": "demo",
        "match_score": 0.88,
        "match_reasons": [
            "Excellent match on React and Node.js experience",
            "PostgreSQL database knowledge aligns perfectly",
            "Your full-stack background is exactly what we need"
        ],
        "missing_skills": ["TypeScript", "Advanced React patterns"]
    }
]


@router.get("/resume")
async def get_demo_resume():
    """Get a sample resume for demo mode."""
    return DEMO_RESUME


@router.get("/jobs")
async def get_demo_jobs():
    """Get sample jobs with match scores for demo mode."""
    return DEMO_JOBS


@router.get("/applications")
async def get_demo_applications():
    """Get sample applications for demo mode."""
    return [
        {
            "id": "demo-app-1",
            "job_id": "demo-job-1",
            "resume_id": "demo-resume-1",
            "status": "applied",
            "job": DEMO_JOBS[0],
            "tailored_resume": "# Alex Johnson\n**Full Stack Engineer**\n\nExperienced software engineer specializing in Python, React, and scalable web applications...",
            "cover_letter": "Dear Stripe Hiring Team,\n\nI'm excited to apply for the Senior Full Stack Engineer position...",
            "created_at": "2026-05-03T14:30:00Z"
        },
        {
            "id": "demo-app-2",
            "job_id": "demo-job-2",
            "resume_id": "demo-resume-1",
            "status": "interviewing",
            "job": DEMO_JOBS[1],
            "tailored_resume": None,
            "cover_letter": None,
            "created_at": "2026-05-02T09:15:00Z"
        }
    ]
