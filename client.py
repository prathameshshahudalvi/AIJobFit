import json
import re
import urllib.request

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from tavily import TavilyClient

from prompt import SYSTEM_PROMPT, build_prompt

MODEL_SIMPLE = "llama-3.3-70b-versatile"
MODEL_DEEP = "openai/gpt-oss-120b"


def _scrape_website(url: str, tavily_api_key: str = "") -> str:
    """Scrape text content from a company website URL."""
    if tavily_api_key:
        client = TavilyClient(api_key=tavily_api_key)
        result = client.extract(urls=[url])
        contents = result.get("results", [])
        if contents:
            return contents[0].get("raw_content", "")[:4000]
    # Fallback: urllib + strip HTML tags
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:4000]


def _fetch_web_interview_questions(
    company_name: str,
    job_role: str,
    tavily_api_key: str,
    api_key: str,
) -> list[dict]:
    """Search Tavily for role-specific questions asked at the company, then extract with LLM."""
    tc = TavilyClient(api_key=tavily_api_key)
    query = f"{company_name} {job_role} interview questions asked candidates experience"
    results = tc.search(query=query, search_depth="advanced", max_results=7)

    raw_results = results.get("results", [])
    if not raw_results:
        return []

    snippets = ""
    for r in raw_results:
        snippets += (
            f"\nSource: {r.get('url', '')}"
            f"\nDate: {r.get('published_date', 'Unknown')}"
            f"\nContent: {r.get('content', '')[:500]}\n---"
        )

    llm = ChatGroq(model=MODEL_SIMPLE, api_key=api_key or None)
    extract_prompt = (
        f"From these web search results about {company_name} {job_role} interviews, "
        f"extract actual specific interview questions asked to candidates.\n\n"
        f"{snippets}\n\n"
        f"Return ONLY a JSON array. Each item: "
        f'[{{"question": "...", "source": "domain only", "date": "date if found, else Unknown"}}]\n'
        f"Extract 5-10 clear, specific questions. No text outside the JSON array."
    )
    msg = llm.invoke([HumanMessage(content=extract_prompt)])
    raw = msg.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except Exception:
        return []


def analyze(
    name: str,
    experience: str,
    skills: str,
    extra_info: str,
    job_description: str,
    company_url: str = "",
    api_key: str = "",
    company_name: str = "",
    job_role: str = "",
    tavily_api_key: str = "",
    deep_search: bool = False,
) -> dict:
    model = MODEL_DEEP if deep_search else MODEL_SIMPLE
    llm = ChatGroq(model=model, api_key=api_key or None)

    company_website_content = ""
    if company_url:
        company_website_content = _scrape_website(company_url, tavily_api_key)

    web_questions = []
    company_interview_context = ""
    if company_name and tavily_api_key:
        web_questions = _fetch_web_interview_questions(company_name, job_role, tavily_api_key, api_key)
        company_interview_context = "\n".join(q.get("question", "") for q in web_questions)

    user_prompt = build_prompt(
        name=name,
        experience=experience,
        skills=skills,
        extra_info=extra_info,
        job_description=job_description,
        company_website_content=company_website_content,
        company_interview_context=company_interview_context,
    )

    message = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ])

    raw = message.content.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw), raw, web_questions


