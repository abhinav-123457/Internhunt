#!/usr/bin/env python3
"""
InternHunt v4 – Resume-aware internship hunter

- Optional resume PDF → auto-detected skills (local sentence-transformers, no API key)
- Preference wizard (roles, stipend, remote, locations)
- Sources: Internshala + Unstop (HTML scraping, limited scope)
- Dark HTML dashboard that auto-opens in your browser
"""

import re
import webbrowser
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import numpy as np
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer  # local model [web:89][web:92]

# ========================= USER PREFS =========================

@dataclass
class UserPrefs:
    wanted_keywords: List[str]
    reject_keywords: List[str]
    prefer_remote: bool
    min_stipend: int
    max_post_age_days: int
    max_results: int
    locations: List[str]


def run_wizard() -> UserPrefs:
    print("=== InternHunt Setup Wizard ===")
    roles = input("Desired roles (comma separated, e.g. python, backend, ml): ").strip()
    roles_list = [r.strip().lower() for r in roles.split(",") if r.strip()]

    extra_keywords = input("Extra skill keywords (comma separated, optional): ").strip()
    extra_list = [k.strip().lower() for k in extra_keywords.split(",") if k.strip()]

    wanted_keywords = roles_list + extra_list
    if not wanted_keywords:
        wanted_keywords = ["python", "backend", "ai", "ml", "data", "full stack"]

    reject = input("Things to avoid (e.g. marketing, hr, sales) [press enter for default]: ").strip()
    if reject:
        reject_keywords = [r.strip().lower() for r in reject.split(",") if r.strip()]
    else:
        reject_keywords = ["marketing", "graphic", "hr", "sales", "content writer", "design", "seo"]

    remote_ans = input("Prefer remote? (y/n) [y]: ").strip().lower()
    prefer_remote = (remote_ans != "n")

    try:
        min_stip = int(input("Minimum stipend per month in ₹ [15000]: ").strip() or "15000")
    except ValueError:
        min_stip = 15000

    try:
        age_days = int(input("Max post age in days [7]: ").strip() or "7")
    except ValueError:
        age_days = 7

    try:
        max_results = int(input("Max results to show [25]: ").strip() or "25")
    except ValueError:
        max_results = 25

    locs = input("Preferred locations (comma separated, or 'any'): ").strip()
    if locs and locs.lower() != "any":
        locations = [l.strip().lower() for l in locs.split(",") if l.strip()]
    else:
        locations = []

    print("\nUsing keywords:", wanted_keywords)
    print("Avoiding:", reject_keywords)
    print("Prefer remote:", prefer_remote)
    print("Min stipend:", min_stip)
    print("Locations filter:", locations or "anywhere")

    return UserPrefs(
        wanted_keywords=wanted_keywords,
        reject_keywords=reject_keywords,
        prefer_remote=prefer_remote,
        min_stipend=min_stip,
        max_post_age_days=age_days,
        max_results=max_results,
        locations=locations,
    )

# ========================= RESUME HELPERS =========================

def extract_resume_text(path: str) -> str:
    try:
        reader = PdfReader(path)  # text extraction via pypdf [web:161][web:166]
        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
        return text
    except Exception as e:
        print("Failed to read resume:", e)
        return ""


SKILL_CANDIDATES = [
    # ML / Data Science
    "data science", "machine learning", "deep learning", "neural networks",
    "computer vision", "natural language processing", "nlp",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "data analysis", "data engineering",

    # Programming languages
    "python", "c++", "java", "javascript", "typescript",

    # Backend / Web
    "django", "flask", "fastapi", "rest api", "api development",
    "backend", "full stack", "frontend",
    "react", "next.js", "node.js", "express",

    # Databases
    "sql", "postgresql", "mysql", "mongodb", "redis",

    # DevOps / Cloud / OS
    "docker", "kubernetes", "linux", "bash",
    "aws", "gcp", "azure", "ci cd", "git",

    # CS fundamentals
    "data structures", "algorithms", "system design",
]


def extract_keywords_from_resume(resume_text: str, top_k: int = 20) -> List[str]:
    """
    Use a local sentence-transformer to rank predefined skills against resume text,
    then return top_k skills with a relaxed similarity threshold.
    """
    if not resume_text.strip():
        return []

    print("Loading local sentence-transformer for resume matching...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # [web:89][web:92][web:172]

    resume_emb = model.encode(resume_text, normalize_embeddings=True)
    skill_embs = model.encode(SKILL_CANDIDATES, normalize_embeddings=True)

    scores = np.dot(skill_embs, resume_emb)
    ranked = sorted(zip(SKILL_CANDIDATES, scores), key=lambda x: x[1], reverse=True)

    THRESHOLD = 0.15  # more forgiving so more skills pass [web:165][web:167]
    skills = [skill for skill, score in ranked[:top_k] if score > THRESHOLD]

    return skills

# ========================= SCRAPER UTILS =========================

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)

def parse_stipend_number(stipend: str) -> int:
    s = stipend.lower()
    nums = re.findall(r"\d+", s.replace(",", ""))
    if not nums:
        return 0
    try:
        return int(nums[0])
    except ValueError:
        return 0

def text_age_to_days(text: str) -> Optional[int]:
    low = text.lower()
    if "just now" in low or "today" in low:
        return 0
    m = re.search(r"(\d+)\s+day", low)
    if m:
        return int(m.group(1))
    return None

def match_score(prefs: UserPrefs, title: str, desc: str, stipend: str, location: str) -> float:
    text = f"{title} {desc} {stipend} {location}".lower()
    score = 0.0

    if any(bad in text for bad in prefs.reject_keywords):
        return -1.0

    for kw in prefs.wanted_keywords:
        if kw in text:
            score += 2.0

    stipend_value = parse_stipend_number(stipend)
    if stipend_value >= prefs.min_stipend > 0:
        score += 2.0
    elif stipend_value == 0:
        score -= 0.5

    if prefs.prefer_remote:
        if "remote" in text or "work from home" in text:
            score += 1.5
        if "on site" in text or "on-site" in text:
            score -= 0.5

    if prefs.locations:
        if any(loc in text for loc in prefs.locations):
            score += 1.0
        else:
            score -= 0.5

    return score

# ========================= SCRAPERS =========================

def scrape_internshala(prefs: UserPrefs) -> List[Dict[str, Any]]:
    url = "https://internshala.com/internships/python,software-development-internship/"
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    listings: List[Dict[str, Any]] = []

    cards = soup.select(".individual_internship") or soup.select(".internship_meta")  # [web:124]
    for card in cards:
        title_el = card.select_one(".job-internship-name") or card.select_one(".profile")
        title = (title_el.text or "").strip() if title_el else "No title"

        company_el = card.select_one(".company-name") or card.select_one(".company_name")
        company = (company_el.text or "").strip() if company_el else "Unknown company"

        stipend_el = card.select_one(".stipend") or card.select_one(".stipend_container")
        stipend = (stipend_el.text or "").strip() if stipend_el else "Not specified"

        location_el = card.select_one(".location_link") or card.select_one(".location")
        location = (location_el.text or "").strip() if location_el else "Location not specified"

        posted_el = card.select_one(".status") or card.select_one(".posted_by")
        posted_text = (posted_el.text or "").strip() if posted_el else ""
        age_days = text_age_to_days(posted_text) or 0
        if prefs.max_post_age_days and age_days > prefs.max_post_age_days:
            continue

        desc_el = card.select_one(".internship_other_details") or card.select_one(".about_company_text")
        desc = (desc_el.text or "").strip() if desc_el else ""

        link_el = card.select_one("a")
        link = "https://internshala.com" + link_el["href"] if link_el and link_el.get("href") else url

        score = match_score(prefs, title, f"{company} {desc}", stipend, location)
        if score <= 0:
            continue

        listings.append(
            {
                "source": "Internshala",
                "title": title,
                "company": company,
                "stipend": stipend,
                "location": location,
                "link": link,
                "score": round(score, 2),
                "posted": posted_text,
            }
        )

    return listings

def scrape_unstop(prefs: UserPrefs) -> List[Dict[str, Any]]:
    """
    Basic scraper for Unstop internships listing page.
    Selectors approximate and may need tweaks if layout changes. [web:145][web:154]
    """
    url = "https://unstop.com/internships"
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    listings: List[Dict[str, Any]] = []

    cards = soup.select(".opp-card") or soup.select("[data-opp-id]")
    for card in cards:
        title_el = card.select_one(".opp-card-title") or card.select_one("h3")
        title = (title_el.text or "").strip() if title_el else "No title"

        company_el = card.select_one(".opp-card-org") or card.select_one(".company-name")
        company = (company_el.text or "").strip() if company_el else "Unknown"

        stipend_el = card.select_one(".stipend") or card.select_one(".opp-card-prize")
        stipend = (stipend_el.text or "").strip() if stipend_el else "Not specified"

        location_el = card.select_one(".opp-card-location") or card.select_one(".location")
        location = (location_el.text or "").strip() if location_el else "Location not specified"

        posted_el = card.select_one(".opp-card-deadline") or card.select_one(".opp-card-days-left")
        posted_text = (posted_el.text or "").strip() if posted_el else ""
        age_days = text_age_to_days(posted_text) or 0
        if prefs.max_post_age_days and age_days > prefs.max_post_age_days:
            continue

        desc_el = card.select_one(".opp-card-desc") or card.select_one("p")
        desc = (desc_el.text or "").strip() if desc_el else ""

        link_el = card.select_one("a")
        href = link_el.get("href") if link_el else ""
        link = "https://unstop.com" + href if href and href.startswith("/") else url

        score = match_score(prefs, title, f"{company} {desc}", stipend, location)
        if score <= 0:
            continue

        listings.append(
            {
                "source": "Unstop",
                "title": title,
                "company": company,
                "stipend": stipend,
                "location": location,
                "link": link,
                "score": round(score, 2),
                "posted": posted_text,
            }
        )

    return listings

# ========================= HTML DASHBOARD =========================

def render_dashboard(prefs: UserPrefs, listings: List[Dict[str, Any]]) -> str:
    cards = ""
    for job in listings:
        badges = f"{job['source']} • {job.get('posted','').strip()}"
        cards += f"""
        <div class="job-card">
            <div class="job-header">
                <div class="job-title">{job['title']}</div>
                <div class="job-score">{job['score']}</div>
            </div>
            <div class="job-meta">
                <span>{job['company']}</span> • <span>{job['location']}</span>
            </div>
            <div class="job-stipend">Stipend: {job['stipend']}</div>
            <div class="job-badges">{badges}</div>
            <a class="job-link" href="{job['link']}" target="_blank">View details</a>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>InternHunt Dashboard</title>
<style>
body {{
  background: radial-gradient(circle at top, #020617 0%, #020314 60%, #000 100%);
  color: #e5e7eb;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  margin: 0;
  padding: 32px 16px;
}}
.wrapper {{
  max-width: 1024px;
  margin: 0 auto;
}}
h1 {{
  font-size: 2.2rem;
  margin-bottom: 4px;
  background: linear-gradient(90deg, #a855f7, #ec4899, #22d3ee);
  -webkit-background-clip: text;
  color: transparent;
}}
.subtitle {{
  font-size: 0.9rem;
  color: #9ca3af;
  margin-bottom: 20px;
}}
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}}
.job-card {{
  background: rgba(15, 23, 42, 0.85);
  border-radius: 18px;
  padding: 14px 16px 16px 16px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  backdrop-filter: blur(16px);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.75);
}}
.job-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}}
.job-title {{
  font-size: 1rem;
  font-weight: 600;
  color: #f9fafb;
  margin-right: 8px;
}}
.job-score {{
  font-size: 0.85rem;
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.8);
  color: #67e8f9;
}}
.job-meta {{
  margin-top: 4px;
  font-size: 0.82rem;
  color: #9ca3af;
}}
.job-stipend {{
  margin-top: 6px;
  font-size: 0.86rem;
  color: #a5b4fc;
}}
.job-badges {{
  margin-top: 4px;
  font-size: 0.75rem;
  color: #6b7280;
}}
.job-link {{
  display: inline-block;
  margin-top: 10px;
  font-size: 0.85rem;
  padding: 6px 10px;
  border-radius: 999px;
  background: linear-gradient(90deg, #4f46e5, #ec4899);
  color: #f9fafb;
  text-decoration: none;
}}
.job-link:hover {{
  filter: brightness(1.1);
}}
</style>
</head>
<body>
<div class="wrapper">
  <h1>InternHunt • Curated internships</h1>
  <div class="subtitle">
    {len(listings)} matches • Keywords: {", ".join(prefs.wanted_keywords)} • Min stipend: ₹{prefs.min_stipend}
  </div>
  <div class="grid">
    {cards if cards else "<p>No strong matches found today.</p>"}
  </div>
</div>
</body>
</html>
"""
    return html

# ========================= MAIN =========================

def main():
    use_resume = input("Do you want to upload a resume for smarter matching? (y/n) [n]: ").strip().lower() == "y"
    resume_keywords: List[str] = []

    if use_resume:
        resume_path = input("Enter path to your resume PDF: ").strip()
        resume_text = extract_resume_text(resume_path)
        if resume_text:
            resume_keywords = extract_keywords_from_resume(resume_text)
            print("Keywords detected from resume:", resume_keywords)
        else:
            print("Could not extract text from resume, will use only wizard preferences.")

    prefs = run_wizard()

    if resume_keywords:
        merged = list(dict.fromkeys(resume_keywords + prefs.wanted_keywords))
        prefs.wanted_keywords = merged
        print("Final WANTED_KEYWORDS (resume + wizard):", prefs.wanted_keywords)

    print("\nFetching internships...\n")

    all_listings: List[Dict[str, Any]] = []

    try:
        ist_list = scrape_internshala(prefs)
        all_listings.extend(ist_list)
        print(f"Internshala: {len(ist_list)} matches.")
    except Exception as e:
        print("Internshala scraper failed:", e)

    try:
        unstop_list = scrape_unstop(prefs)
        all_listings.extend(unstop_list)
        print(f"Unstop: {len(unstop_list)} matches.")
    except Exception as e:
        print("Unstop scraper failed:", e)

    if not all_listings:
        print("No matching internships found.")
        return

    all_listings.sort(
        key=lambda x: (x["score"], parse_stipend_number(x["stipend"])),
        reverse=True,
    )
    shortlisted = all_listings[: prefs.max_results]

    html = render_dashboard(prefs, shortlisted)
    out_path = "internhunt_dashboard.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nSaved dashboard to {out_path}. Opening in browser...")

    url = "file://" + str(__import__("pathlib").Path(out_path).resolve())
    webbrowser.open(url, new=1, autoraise=True)  # [web:79][web:169]

    print("Done.")

if __name__ == "__main__":
    main()
