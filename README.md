# InternHunt v6

**Automated Internship Discovery for Indian Job Platforms**

InternHunt v6 is a Python CLI application that automates the process of discovering relevant internship opportunities across multiple Indian job platforms. It extracts skills from your resume, collects your preferences through a simplified wizard, scrapes listings using Selenium for JavaScript-heavy sites, and presents results in a beautiful dark-mode HTML dashboard.

## Features

- 🎯 **Smart Resume Parsing**: Extracts 20-50 skills from PDF resumes using AI-powered semantic matching
- 🔍 **Multi-Platform Scraping**: Searches across 4 major Indian internship platforms
  - Internshala (5 pages)
  - LinkedIn (5 pages with OR logic for broader results)
  - Naukri (5 pages)
  - Unstop (5 pages)
- 🌐 **Selenium-Based Scraping**: Handles JavaScript-heavy websites with automatic ChromeDriver management
- 📊 **Keyword-Based Filtering**: Ranks opportunities based on keyword matches and resume skills
- 🎨 **Dark Mode Dashboard**: Generates a responsive HTML dashboard with Tailwind CSS styling
- 🚀 **Auto-Launch**: Opens results automatically in your default browser
- ♻️ **Smart Deduplication**: Removes duplicate listings across platforms
- 📈 **High Volume Results**: Scrapes 400+ listings, displays up to 100 results
- 🛡️ **Ethical Scraping**: Implements rate limiting and respectful scraping practices

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download

```bash
git clone <repository-url>
cd internhunt-v6
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `pypdf` - PDF text extraction
- `sentence-transformers` - AI-powered skill matching (extracts 20-50 skills)
- `numpy` - Numerical operations
- `selenium` - Browser automation for JavaScript-heavy sites
- `webdriver-manager` - Automatic ChromeDriver management
- `hypothesis` - Property-based testing (for development)

### Step 3: Verify Installation

```bash
python internhunt.py --help
```

You should see the help message with usage instructions.

## Usage

### Basic Usage (Without Resume)

Run the application and follow the simplified wizard:

```bash
python internhunt.py
```

The wizard will prompt you for only 4 questions:
- **Wanted keywords** (e.g., "python, ml, gen ai, data science")
- **Reject keywords** (e.g., "hr, sales, marketing")
- **Maximum post age** (in days, e.g., 30)
- **Maximum results** (default: 100)

**Note**: The app now shows ALL listings regardless of:
- Stipend amount (all stipend levels shown)
- Location (all locations shown)
- Remote work type (all work types shown)

### With Resume Parsing (Recommended)

Provide your resume PDF to automatically extract 20-50 skills:

```bash
python internhunt.py path/to/your/resume.pdf
```

Or:

```bash
python internhunt.py --resume path/to/your/resume.pdf
```

The system will:
1. Extract text from your PDF
2. Use AI to identify 20-50 relevant skills
3. Use these skills for scoring internship matches
4. Automatically expand abbreviations (ml → machine learning, ai → artificial intelligence)

### Example Session

```bash
$ python internhunt.py myresume.pdf

============================================================
🎯 InternHunt v6 - Automated Internship Discovery
============================================================

📄 Parsing resume: myresume.pdf
    Loading AI model for skill extraction...
✓ Extracted 20 skills from resume

============================================================
InternHunt v6 - Preference Wizard
============================================================

Enter wanted keywords (comma-separated): python, ml, gen ai, data analytics
Enter reject keywords (comma-separated): hr, sales, marketing
Enter maximum post age in days (e.g., 30): 30
Enter maximum number of results (default 100): 100

============================================================
Preferences saved! Starting internship search...
============================================================

🔍 Scraping internship listings from multiple platforms...
This may take 20-30 seconds...

Scraping from: Internshala, Unstop, LinkedIn, Naukri

✓ Internshala: 130 listings
✓ LinkedIn: 118 listings (using OR logic for broader results)
✓ Naukri: 40 listings
✓ Unstop: 0 listings

✓ Scraped 288 total listings

⚖️  Scoring and filtering listings...
✓ 232 listings passed filtering

🔄 Removing duplicates...
✓ Removed 88 duplicate(s)

📊 Limiting results to top 100 listings

📊 Generating HTML dashboard...
✓ Dashboard generated: internhunt_results_20251207_130200.html

🌐 Opening dashboard in browser...
✓ Dashboard opened in browser

============================================================
📈 Execution Summary
============================================================
Total listings scraped:     288
After filtering:            232
After deduplication:        100
Dashboard location:         output/internhunt_results_20251207_130200.html
============================================================
✨ Happy job hunting! ✨
```

## Output
[](!output.mp4)

The application generates a beautiful dark-mode HTML dashboard in the `output/` directory with:

- **Modern Dark Theme**: Built with Tailwind CSS and shadcn/ui styling
- **Job Cards**: Each listing displayed as a card with:
  - Job title and company
  - Stipend (formatted in INR with ₹ symbol)
  - Location
  - Platform badge (Internshala, LinkedIn, Naukri, Unstop)
  - Direct "View Details" link to apply
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Sorted by Relevance**: Highest scoring opportunities first (based on keyword matches)
- **No Confusing Scores**: Clean interface without numeric score badges
- **Hover Effects**: Smooth animations and shimmer effects on card hover

## Configuration

### Skill Library

The system includes 50+ predefined skills across categories:
- Programming Languages (Python, Java, JavaScript, C++, Go, Rust, etc.)
- ML/AI (Machine Learning, Deep Learning, NLP, Computer Vision, TensorFlow, PyTorch)
- Web Development (React, Angular, Vue, Node.js, Django, Flask, FastAPI)
- Databases (SQL, PostgreSQL, MongoDB, Redis, MySQL)
- Cloud (AWS, Azure, GCP, Docker, Kubernetes)
- Tools (Git, Linux, CI/CD, Testing)

You can modify the skill library in `src/skill_library.py`.

### Scoring System

Listings are scored based on:
- **Wanted Keywords**: +10 points per match (uses word boundary matching to avoid false positives)
- **Resume Skills**: +3 points per match
- **Stipend**: Up to +3 points (proportional bonus, but NOT used for filtering)
- **Remote Work**: Not used for filtering (all work types shown)
- **Location**: Not used for filtering (all locations shown)

**Keyword Expansion**: The system automatically expands abbreviations:
- `ml` → `ml`, `machine learning`
- `ai` → `ai`, `artificial intelligence`
- `nlp` → `nlp`, `natural language processing`
- `genai` → `genai`, `gen ai`, `generative ai`
- And many more...

**Filtering**: Only reject keywords are used for filtering. All listings matching at least one wanted keyword are shown.

### Selenium Configuration

The application uses Selenium for JavaScript-heavy websites:
- **Automatic ChromeDriver Management**: No manual driver installation needed
- **Headless Mode**: Runs in background without opening browser windows
- **Smart Timeouts**: 15 second page load timeout, 2 second delays between requests
- **Retry Logic**: 2 retries on failure for reliability

### Rate Limiting

The scraper implements ethical practices:
- Minimum 2.0 second delay between requests to the same domain
- 15 second timeout per request
- 2 retries on failure
- Respectful User-Agent headers
- Scrapes 5 pages per platform (not excessive)

## Project Structure

```
internhunt-v6/
├── internhunt.py              # CLI entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── src/
│   ├── __init__.py
│   ├── main.py               # Main application orchestrator
│   ├── skill_library.py      # Predefined skills (50+ skills)
│   ├── resume_parser.py      # PDF parsing and skill extraction (20-50 skills)
│   ├── preference_wizard.py  # Simplified 4-question wizard
│   ├── scraper_engine.py     # Scraping orchestrator
│   ├── scoring_engine.py     # Keyword-based scoring with expansion
│   ├── deduplicator.py       # Smart duplicate removal
│   ├── dashboard_generator.py # Dark mode HTML generation
│   ├── browser_launcher.py   # Browser auto-launch
│   ├── logging_config.py     # Logging configuration
│   └── scrapers/
│       ├── base_scraper.py   # Base scraper class
│       ├── selenium_scraper.py # Selenium base class
│       ├── internshala_scraper.py # 5 pages
│       ├── linkedin_scraper.py    # 5 pages with OR logic
│       ├── naukri_scraper.py      # 5 pages with Selenium
│       └── unstop_scraper.py      # 5 pages with Selenium
├── tests/                     # Unit and property tests
├── output/                    # Generated dashboards
└── internhunt.log            # Application logs
```

## Troubleshooting

### Resume Parsing Issues

**Problem**: "Unable to parse resume"
- **Solution**: Ensure your PDF is not encrypted or corrupted. Try opening it in a PDF reader first.

**Problem**: "No skills extracted"
- **Solution**: The system requires text-based PDFs. If your resume is image-based, convert it to text first.

### Scraping Issues

**Problem**: "Failed to scrape [Platform]"
- **Solution**: This is normal. The scraper continues with other platforms. Check `internhunt.log` for details.

**Problem**: LinkedIn returns 0 results or shows anti-bot protection
- **Solution**: LinkedIn has aggressive anti-bot protection. This is expected behavior. The app will still work with other platforms (Internshala, Naukri, Unstop).

**Problem**: ChromeDriver issues
- **Solution**: The app uses `webdriver-manager` to automatically download and manage ChromeDriver. Ensure you have Chrome browser installed.

**Problem**: "No results found"
- **Solution**: Try:
  - Broadening your keywords (use more general terms)
  - Increasing maximum post age (try 60 or 90 days)
  - Using abbreviations (ml, ai, nlp) which auto-expand

### Browser Launch Issues

**Problem**: Dashboard doesn't open automatically
- **Solution**: The file path is printed. Open it manually in your browser.

### Performance Issues

**Problem**: Scraping takes too long
- **Solution**: This is expected (20-40 seconds) due to:
  - Selenium browser automation for JavaScript sites
  - Rate limiting (2 second delays)
  - Scraping 5 pages per platform
  - This ensures ethical scraping and avoids being blocked

## Ethical Scraping Practices

InternHunt v6 follows responsible scraping practices:

1. **Rate Limiting**: Minimum 2.0 second delays between requests
2. **Timeouts**: 15 second timeout prevents hanging
3. **User-Agent**: Identifies as a browser, not a bot
4. **Error Handling**: Gracefully handles failures with 2 retries maximum
5. **Limited Pages**: Only scrapes 5 pages per platform (not excessive)
6. **No Credentials**: Never stores or transmits user credentials
7. **Public Data Only**: Only accesses publicly available listings
8. **Headless Mode**: Selenium runs in background without disrupting users

### Legal Considerations

- This tool is for **personal use only**
- Do not use for commercial purposes without permission
- Respect the terms of service of each platform
- Do not scrape excessively or cause server load
- Use responsibly and ethically
- Some platforms (like LinkedIn) may block automated access - this is expected

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_resume_parser.py

# Run with coverage
pytest --cov=src tests/

# Run property-based tests
pytest tests/test_*_properties.py
```

### Adding New Scrapers

For static websites (HTML-based):
1. Create a new scraper class in `src/scrapers/`
2. Inherit from `BaseScraper`
3. Implement the `scrape()` method
4. Add to `ScraperEngine` in `src/scraper_engine.py`

For JavaScript-heavy websites:
1. Create a new scraper class in `src/scrapers/`
2. Inherit from `SeleniumScraper`
3. Implement the `scrape()` method
4. Add to `ScraperEngine` in `src/scraper_engine.py`

Example (Selenium):

```python
from src.scrapers.selenium_scraper import SeleniumScraper

class NewPlatformScraper(SeleniumScraper):
    def scrape(self, preferences):
        driver = self.get_driver()
        # Use driver.get(), driver.find_elements(), etc.
        # Implementation
        pass
```

### Logging

Logs are written to `internhunt.log` with levels:
- **ERROR**: Scraping failures, parsing errors
- **WARNING**: Rate limiting, missing data
- **INFO**: Progress updates
- **DEBUG**: Detailed scraping data

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note**: This tool is intended for personal use. Please respect the terms of service of each platform and use responsibly and ethically.

## Key Improvements in v6

- ✅ **Simplified Wizard**: Reduced from 6 questions to 4 essential questions
- ✅ **No Filtering by Stipend/Location/Remote**: Shows ALL listings for maximum opportunities
- ✅ **Selenium Integration**: Handles JavaScript-heavy sites (LinkedIn, Naukri, Unstop)
- ✅ **Keyword Expansion**: Automatically expands abbreviations (ml → machine learning)
- ✅ **Word Boundary Matching**: Prevents false positives (hr won't match "three")
- ✅ **LinkedIn OR Logic**: Uses "python OR ml OR ai" for broader search results
- ✅ **Increased Volume**: Scrapes 400+ listings, displays up to 100 results
- ✅ **Dark Mode Dashboard**: Modern Tailwind CSS design with no confusing score badges
- ✅ **Smart Deduplication**: Removes duplicate listings across platforms
- ✅ **Better Skill Extraction**: Extracts 20-50 skills from resume (not just 10)

## Acknowledgments

- Built with Python and open-source libraries
- Uses SentenceTransformers for AI-powered skill matching (20-50 skills)
- Selenium and webdriver-manager for JavaScript site automation
- Tailwind CSS and shadcn/ui for beautiful dark mode dashboard
- Designed for the Indian internship market

## Support

For issues, questions, or suggestions:
- Check the troubleshooting section
- Review `internhunt.log` for detailed error messages
- Open an issue on the repository

---

**Happy Internship Hunting! 🚀**
