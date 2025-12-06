# InternHunt – Resume‑Aware Internship Hunter

> “I hate scrolling through 200 random internship listings, so I built InternHunt to find the few that actually fit my resume.”

InternHunt is a local Python tool that reads your preferences (and optionally your resume) and surfaces the most relevant internships from Internshala and Unstop in a dark, clickable HTML dashboard.

---

## Features

- 🔍 **Preference wizard**
  - Desired roles and skills (e.g. python, backend, ml)
  - Things to avoid (e.g. marketing, HR, design)
  - Remote vs on‑site preference
  - Minimum stipend (₹)
  - Maximum post age (in days)
  - Preferred locations

- 📄 **Resume‑aware matching (optional)**
  - Reads your resume PDF using `pypdf` and extracts raw text. [web:161][web:166]
  - Uses a local `sentence-transformers/all-MiniLM-L6-v2` model to infer top skills from your resume (no API key). [web:105][web:260][web:268]
  - Merges resume‑derived skills with wizard keywords to build a richer match profile.

- 🌐 **Sources (HTML scraping, limited scope)**
  - Internshala engineering/software internships page. [web:266]
  - Unstop internships listing page. [web:145][web:154]
  - Scrapes title, company, stipend, location, basic description, and link into a unified job format.

- 🧠 **Scoring engine**
  - Rewards:
    - Presence of wanted keywords in title/description.
    - Stipend ≥ your minimum.
    - Remote roles if you prefer remote.
    - Locations that match your preferences.
  - Penalizes:
    - Reject keywords (e.g. “marketing”, “content writer”).
    - Missing stipend or mismatched locations.
  - Sorts by `(score, stipend)` and keeps top N results.

- 🌓 **Dark HTML dashboard**
  - Generates `internhunt_dashboard.html` with:
    - Gradient dark background.
    - Cards for each internship (title, company, location, stipend, score, source, posted text).
  - Automatically opens the dashboard in your default browser via `webbrowser`. [web:79][web:169]

---

## Installation

Clone the repo and install dependencies:

