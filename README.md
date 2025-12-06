# InternHunt – Resume‑Aware Internship Hunter

> “I hate scrolling through 200 random internship listings, so I built InternHunt to find the few that actually fit my resume.”

InternHunt is a local Python tool that reads your preferences (and optionally your resume) and surfaces the most relevant internships, clickable HTML dashboard.

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
```
https://github.com/abhinav-123457/Internhunt
```
Open the Internhunt Folder
```
cd internhunt
```
Install the requirements file
```
pip install -r requirements.txt
```

`requirements.txt` includes:

- `requests` – HTTP requests  
- `beautifulsoup4` – HTML parsing  
- `pypdf` – resume PDF text extraction [web:161][web:166]  
- `sentence-transformers` – local embedding model (`all-MiniLM-L6-v2`) [web:105][web:260][web:268]  
- `numpy` – vector math for similarity scoring  

---

## Usage

From the project root:
```
python internhunt.py
```

Flow:

1. **Resume (optional)**
   - The script asks:  
     `Do you want to upload a resume for smarter matching? (y/n)`  
   - If you choose `y`, enter the path to your resume PDF (e.g. `resume.pdf` or full path).
   - InternHunt extracts text and infers top skills using a local sentence‑transformer model.

2. **Preference wizard**
   - Desired roles (comma‑separated).
   - Extra skill keywords (optional).
   - Things to avoid (or press Enter to use defaults).
   - Remote preference (y/n).
   - Minimum stipend (₹).
   - Maximum post age (days).
   - Preferred locations (or `any`).

3. **Scraping & ranking**
   - InternHunt scrapes Internshala and Unstop with a browser‑like User‑Agent and basic selectors. [web:145][web:154][web:266]
   - It scores each listing with `match_score(...)` and filters out low/negative scores.

4. **Dashboard**
   - Saves `internhunt_dashboard.html` in the project folder.
   - Automatically opens it in your default browser with `file://...`. [web:79][web:169]

If no matching internships are found, the script prints a message and exits.

---

## How it works (high level)

- `UserPrefs` dataclass stores your preferences.
- `extract_resume_text()` uses `PdfReader` from `pypdf` to read PDF pages into text. [web:161][web:166]
- `extract_keywords_from_resume()` encodes resume text and a predefined `SKILL_CANDIDATES` list with `all-MiniLM-L6-v2`, then keeps the top skills above a similarity threshold. [web:105][web:260][web:268]
- `scrape_internshala()` and `scrape_unstop()` request the listing pages and parse cards with BeautifulSoup. [web:145][web:154][web:266]
- `match_score()` combines keywords, stipend, remote, and location into a single float.
- `render_dashboard()` builds a responsive dark‑mode HTML grid of cards.

---

## Kiro spec‑driven setup

This project is structured to work nicely with the Kiro AI IDE:

- Specs live under `.kiro/specs/internhunt/`:
  - `requirements.md` – problem and scope
  - `design.md` – architecture and data model
  - `tasks.md` – implementation and polish tasks

You can open this folder in Kiro and use the spec to:

- Refactor functions.
- Add docstrings.
- Generate tests for the scoring logic.

---

## Notes & limitations

- Selectors for Internshala and Unstop are approximate and may need updates if their HTML changes. [web:145][web:154][web:266]
- Resume skill extraction depends on the quality and structure of your PDF.
- No LinkedIn or large job‑board scraping is included, to stay within safe, realistic scope.
- Everything runs locally; there are no external AI API calls, only a local sentence‑transformer model load.

---

## License
[MIT License](LICENSE) © 2025 [abhinav-123457]

