import os
import streamlit as st

from client import analyze

st.set_page_config(
    page_title="AI Resume & Job Matcher",
    page_icon="🤖",
    layout="wide",
)

st.title("AI Job Matcher")

DUMMY_NAME = "Your Name"


# ── Sidebar: Input Form ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get your key at console.groq.com",
    )
    tavily_api_key = st.text_input(
        "Tavily API Key (optional)",
        type="password",
        placeholder="tvly-...",
        help="Enables real interview Q&A search from the web. Get your key at app.tavily.com",
    )
    search_mode = st.radio(
        "Search Mode",
        options=["Simple", "Deep Search"],
        help="Simple: fast & free (Llama 3.3 70B) · Deep Search: more accurate (GPT-o3 120B)",
        horizontal=True,
    )
    st.divider()

    st.header("Candidate Profile")

    experience = st.number_input("Years of Experience", min_value=0, max_value=30, value=2, step=1)
    skills = st.text_area(
        "Skills (comma-separated)",
        placeholder="e.g. Python, LangChain, FastAPI, PostgreSQL, RAG",
        height=100,
    )
    extra_info = st.text_area(
        "Additional Info (optional)",
        placeholder="Certifications, notable projects, achievements...",
        height=80,
    )

    st.header("Job Details")
    job_role = st.text_input(
        "Job Role / Title",
        placeholder="e.g. Machine Learning Engineer, Backend Developer",
    )
    company_name = st.text_input(
        "Company Name (optional)",
        placeholder="e.g. Google, Stripe, OpenAI",
        help="If provided, Tavily will search for real interview questions asked at this company.",
    )
    job_description = st.text_area(
        "Job Description",
        placeholder="Paste the full job description here...",
        height=200,
    )
    company_url = st.text_input(
        "Company Website (optional)",
        placeholder="e.g. https://openai.com",
        help="If provided, the website will be scraped to generate a company summary in Job Summary.",
    )

    analyze_btn = st.button("Analyze", type="primary", use_container_width=True)

# ── Validation & API key check ─────────────────────────────────────────────────
if analyze_btn:
    resolved_api_key = groq_api_key.strip() or os.environ.get("GROQ_API_KEY", "")
    if not resolved_api_key:
        st.error("Please enter your Groq API key in the sidebar.")
        st.stop()

    if not skills.strip():
        st.error("Please enter at least one skill.")
        st.stop()

    if not job_description.strip():
        st.error("Please paste a job description.")
        st.stop()

    # ── Call Groq API ─────────────────────────────────────────────────────────
    spinner_msg = (
        f"Searching web for {company_name.strip()} interview questions & analyzing your profile..."
        if company_name.strip() and tavily_api_key.strip()
        else "Analyzing your profile against the job description..."
    )
    with st.spinner(spinner_msg):
        try:
            data, raw_response, web_questions = analyze(
                name=DUMMY_NAME,
                experience=str(experience),
                skills=skills.strip(),
                extra_info=extra_info.strip(),
                job_description=job_description.strip(),
                company_url=company_url.strip(),
                api_key=resolved_api_key,
                company_name=company_name.strip(),
                job_role=job_role.strip(),
                tavily_api_key=tavily_api_key.strip(),
                deep_search=search_mode == "Deep Search",
            )
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            with st.expander("Raw API response"):
                st.text(str(e))
            st.stop()

    st.success("Analysis complete!")


    # ── Results Tabs ───────────────────────────────────────────────────────────
    tabs = st.tabs([
        "Job Summary",
        "Match Score",
        "Tailored Resume",
        "Interview Prep",
        "Take My Interview",
    ])

    # ── Tab 1: Job Summary ─────────────────────────────────────────────────────
    with tabs[0]:
        st.subheader("Job Summary")
        job_summary = data.get("job_summary", {})

        st.markdown("**Role Overview**")
        for point in job_summary.get("overview", []):
            st.markdown(f"- {point}")

        st.markdown("**Key Technologies**")
        tech_cols = st.columns(4)
        for i, tech in enumerate(job_summary.get("technologies", [])):
            tech_cols[i % 4].markdown(
                f"<span style='background:#1e3a5f;color:#90caf9;padding:4px 10px;"
                f"border-radius:12px;font-size:13px'>{tech}</span>",
                unsafe_allow_html=True,
            )

        company_summary = job_summary.get("company_summary", [])
        if company_summary:
            st.divider()
            st.markdown("**About the Company**")
            for point in company_summary:
                st.markdown(f"- {point}")

    # ── Tab 2: Match Score ─────────────────────────────────────────────────────
    with tabs[1]:
        st.subheader("Match Analysis")
        match = data.get("match_analysis", {})
        score = match.get("score", 0)

        color = "#4caf50" if score >= 70 else "#ff9800" if score >= 40 else "#f44336"
        st.markdown(
            f"<h1 style='color:{color};font-size:80px;text-align:center'>{score}%</h1>",
            unsafe_allow_html=True,
        )
        st.progress(score / 100)

        st.markdown(f"**{match.get('explanation', '')}**")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Strengths**")
            for s in match.get("strengths", []):
                st.markdown(f"✅ {s}")
        with col2:
            st.markdown("**Weaknesses**")
            for w in match.get("weaknesses", []):
                st.markdown(f"⚠️ {w}")

    # ── Tab 3: Tailored Resume ─────────────────────────────────────────────────
    with tabs[2]:
        st.subheader("Tailored Resume")
        st.caption("Crafted specifically for this company and role.")
        tr = data.get("tailored_resume", {})

        st.markdown(
            f"<h3 style='margin-bottom:2px'>{DUMMY_NAME}</h3>"
            f"<p style='color:#90caf9;font-size:15px;margin-top:0'>{tr.get('headline', '')}</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        st.markdown("**Summary**")
        st.write(tr.get("summary", ""))

        st.markdown("**Skills**")
        skill_cols = st.columns(4)
        for i, skill in enumerate(tr.get("skills", [])):
            skill_cols[i % 4].markdown(
                f"<span style='background:#1e3a5f;color:#90caf9;padding:3px 9px;"
                f"border-radius:10px;font-size:13px;display:inline-block;margin:2px'>{skill}</span>",
                unsafe_allow_html=True,
            )

        st.markdown("**Experience**")
        for exp in tr.get("experience", []):
            duration_html = f"<span style='color:#aaa;font-size:13px'>{exp.get('duration', '')}</span>"
            st.markdown(
                f"<div style='margin-bottom:4px'>"
                f"<strong>{exp.get('title', '')}</strong> &nbsp;·&nbsp; {exp.get('company', '')} &nbsp; {duration_html}"
                f"</div>",
                unsafe_allow_html=True,
            )
            for bullet in exp.get("bullets", []):
                st.markdown(f"- {bullet}")
            st.write("")

        st.markdown("**Projects**")
        for proj in tr.get("projects", []):
            name_str = proj.get("name", "")
            tagline = proj.get("tagline", "")
            description = proj.get("description", "")
            tech = ", ".join(proj.get("tech_stack", []))
            tagline_html = f" <span style='color:#90caf9'>— {tagline}</span>" if tagline else ""
            st.markdown(
                f"<div style='border-left:3px solid #90caf9;padding:8px 12px;margin-bottom:12px'>"
                f"<strong>{name_str}</strong>{tagline_html}"
                f"<br><small style='color:#aaa'>{description}</small>"
                f"<br><span style='font-size:12px;color:#80cbc4'>{tech}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("**Education**")
        st.write(tr.get("education", ""))


    # ── Tab 4: Interview Prep ──────────────────────────────────────────────────
    with tabs[3]:
        st.subheader("Interview Preparation")

        # ── Previously asked at company (Tavily) ──────────────────────────────
        if web_questions:
            st.markdown(f"#### Previously Asked at {company_name.strip() or 'Company'}")
            st.caption("Sourced from the web via Tavily Search.")
            for i, item in enumerate(web_questions, 1):
                q_text = item.get("question", "")
                source = item.get("source", "Unknown source")
                date = item.get("date", "Unknown date")
                with st.container():
                    st.markdown(f"**{i}.** {q_text}")
                    st.markdown(
                        f"<span style='background:#1a3a1a;color:#a5d6a7;padding:2px 8px;"
                        f"border-radius:8px;font-size:12px'>🌐 {source}</span>&nbsp;"
                        f"<span style='background:#2a2a1a;color:#fff176;padding:2px 8px;"
                        f"border-radius:8px;font-size:12px'>📅 {date}</span>",
                        unsafe_allow_html=True,
                    )
                    st.write("")
            st.divider()
        elif not company_name.strip() and not tavily_api_key.strip():
            st.warning(
                "Please add **Tavily API Key** and **Company Name** to search questions this company could ask you."
            )
            st.divider()

        # ── AI-generated questions ─────────────────────────────────────────────
        st.markdown("#### AI-Generated Questions")
        st.caption("Asked by AI — based on the job description and role.")
        iq = data.get("interview_questions", {})

        easy_tab, med_tab, hard_tab = st.tabs(["Easy", "Medium", "Hard"])

        with easy_tab:
            for i, q in enumerate(iq.get("easy", []), 1):
                st.markdown(f"**{i}.** {q}")

        with med_tab:
            for i, q in enumerate(iq.get("medium", []), 1):
                st.markdown(f"**{i}.** {q}")

        with hard_tab:
            for i, q in enumerate(iq.get("hard", []), 1):
                st.markdown(f"**{i}.** {q}")

    # ── Tab 5: Take My Interview ───────────────────────────────────────────────
    with tabs[4]:
        st.subheader("Take My Interview")
        st.info("🚧 Work in Progress")

else:
    st.info("Fill in your profile and job description in the sidebar, then click **Analyze**.")
