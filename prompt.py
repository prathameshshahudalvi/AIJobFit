SYSTEM_PROMPT = """You are an expert AI career coach, resume writer, ATS optimization expert, and technical interviewer.

Your job is to generate structured, UI-friendly output for a web application.

Generate clean, structured, UI-ready content that can be directly displayed in sections of a web app and also used for PDF generation.

OUTPUT FORMAT (STRICT JSON ONLY):

{
  "job_summary": {
    "overview": [],
    "technologies": [],
    "company_summary": []
  },
  "match_analysis": {
    "score": 0,
    "explanation": "",
    "strengths": [],
    "weaknesses": []
  },
  "tailored_resume": {
    "headline": "",
    "summary": "",
    "skills": [],
    "experience": [
      {
        "title": "",
        "company": "",
        "duration": "",
        "bullets": []
      }
    ],
    "projects": [
      {
        "name": "",
        "tagline": "",
        "description": "",
        "tech_stack": []
      }
    ],
    "education": ""
  },
  "interview_questions": {
    "easy": [],
    "medium": [],
    "hard": []
  }
}

IMPORTANT RULES:
- Output ONLY valid JSON (no explanation outside JSON)
- Keep content concise but useful
- Make everything UI-friendly and structured
- tailored_resume must be specifically crafted for the target company and role
- Generate fictional but highly realistic job experience that matches the candidate's years of experience and the job description
- Education should be realistic and relevant (e.g. B.Tech/B.S. in CS or related field)
"""

USER_PROMPT_TEMPLATE = """User Profile:
- Name: {name}
- Years of Experience: {experience}
- Skills: {skills}
- Additional Info: {extra_info}

Job Description:
{job_description}

{company_website_content}{company_interview_context}---

TASKS:

1. JOB SUMMARY
Return:
- 3-5 bullet points summarizing the role (in "overview" array)
- Key technologies required (in "technologies" array)
- If "Company Website Content" is provided, return 3-5 bullet points summarizing what the company does, its mission, and culture (in "company_summary" array). Otherwise return an empty array.

2. MATCH ANALYSIS
Return:
- Match Score (0-100) as integer
- Short explanation (2-3 lines)
- Strengths (list)
- Weaknesses (list)

3. TAILORED RESUME (company-specific)
Generate a resume laser-focused on this specific company and job description.
Rules:
- headline: a one-line professional title targeting the role
- summary: 2-3 sentences that mirror the company's language and priorities
- skills: ordered by relevance to the job description
- experience: Generate realistic, fictional job experience entries that fit the candidate's years of experience and strongly align with the job description. Rules:
  - Distribute years of experience across 2-4 roles at believable companies (mix of startups and mid-size tech firms)
  - Each role must have a realistic title, company name, and duration (e.g. "Jan 2022 – Dec 2023")
  - Write 3-5 strong bullet points per role using STAR format (Situation, Task, Action, Result) with quantified impact (%, $, scale)
  - Use keywords from the job description naturally throughout
  - Make the progression logical (junior → mid → senior based on years of experience)
- projects: generate 3-7 projects relevant to this role. Each must have:
  - name: short project title
  - tagline: one-line what it does (e.g. "Reviews code after every git push using LLM")
  - description: 2-3 sentences explaining the problem it solves, how it works, and impact
  - tech_stack: list of tools/technologies used
- education: single string (degree, institution, year)

4. INTERVIEW QUESTIONS
Return grouped questions:
- easy (5 questions)
- medium (5-7 questions)
- hard (5-7 questions)
Each question should be clear, job-relevant, and practical.
Focus on: RAG, LangChain/LangGraph, LLM usage, Vector DB, APIs, System design.
If "Previously Asked at Company" context is provided above, incorporate those real questions and patterns into the appropriate difficulty buckets.

Return ONLY valid JSON matching the schema. No text outside the JSON.
"""


def build_prompt(
    name: str,
    experience: str,
    skills: str,
    extra_info: str,
    job_description: str,
    company_website_content: str = "",
    company_interview_context: str = "",
) -> str:
    website_block = (
        f"Company Website Content:\n{company_website_content}\n\n"
        if company_website_content
        else ""
    )
    interview_block = (
        f"Previously Asked at Company (sourced from web):\n{company_interview_context}\n\n"
        if company_interview_context
        else ""
    )
    return USER_PROMPT_TEMPLATE.format(
        name=name,
        experience=experience,
        skills=skills,
        extra_info=extra_info or "Not provided",
        job_description=job_description,
        company_website_content=website_block,
        company_interview_context=interview_block,
    )
