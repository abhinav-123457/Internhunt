# Design Document

## Overview

InternHunt v6 is a Python CLI application that automates internship discovery across multiple Indian job platforms. The system follows a pipeline architecture: Resume Parsing → Preference Collection → Web Scraping → Scoring & Filtering → Deduplication → Dashboard Generation → Browser Launch.

The application uses SentenceTransformer for semantic skill matching, BeautifulSoup for HTML parsing, and generates a responsive HTML dashboard with CSS Grid. The design emphasizes modularity, error resilience, and ethical scraping practices.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   CLI Entry     │
│     Point       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Resume Parser   │ (Optional)
│  - PDF Extract  │
│  - Embeddings   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Preference      │
│    Wizard       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Scraper Engine  │
│  - 6 Platforms  │
│  - Rate Limit   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Scoring Engine  │
│  - Keywords     │
│  - Stipend      │
│  - Location     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Deduplicator    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │
│   Generator     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Browser Launcher│
└─────────────────┘
```

### Component Interaction

- **Sequential Pipeline**: Each component processes data and passes results to the next stage
- **Error Isolation**: Failures in one scraper or parser don't affect other components
- **Stateless Processing**: Each component operates independently on input data
- **Configuration Flow**: User preferences flow through the pipeline to guide filtering and scoring

## Components and Interfaces

### 1. Skill Library Module

**Purpose**: Provides predefined technical and professional skills for matching

**Interface**:
```python
class SkillLibrary:
    @staticmethod
    def get_all_skills() -> List[str]:
        """Returns list of 50+ predefined skills"""
        pass
    
    @staticmethod
    def get_skill_categories() -> Dict[str, List[str]]:
        """Returns skills organized by category"""
        pass
```

**Skills Categories**:
- Programming Languages: Python, Java, JavaScript, C++, Go, Rust, etc.
- ML/AI: Machine Learning, Deep Learning, NLP, Computer Vision, TensorFlow, PyTorch
- Web Development: React, Angular, Vue, Node.js, Django, Flask, FastAPI
- Databases: SQL, PostgreSQL, MongoDB, Redis, MySQL
- Cloud: AWS, Azure, GCP, Docker, Kubernetes
- Tools: Git, Linux, CI/CD, Testing

### 2. Resume Parser Module

**Purpose**: Extracts skills from PDF resumes using semantic similarity

**Interface**:
```python
@dataclass
class ResumeSkills:
    extracted_skills: List[str]
    confidence_scores: Dict[str, float]

class ResumeParser:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize with SentenceTransformer model"""
        pass
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        pass
    
    def match_skills(self, resume_text: str, threshold: float = 0.5) -> ResumeSkills:
        """Match resume text against skill library using embeddings"""
        pass
```

**Implementation Details**:
- Use `pypdf.PdfReader` for text extraction
- Use `sentence_transformers.SentenceTransformer` for embeddings
- Compute cosine similarity between resume text chunks and skill terms
- Return top 10-50 skills above similarity threshold
- Handle multi-page PDFs by concatenating text

### 3. Preference Wizard Module

**Purpose**: Interactive CLI for collecting user search preferences

**Interface**:
```python
@dataclass
class UserPreferences:
    wanted_keywords: List[str]
    reject_keywords: List[str]
    remote_preference: str  # 'yes', 'no', 'any'
    min_stipend: int
    max_post_age_days: int
    max_results: int
    preferred_locations: List[str]
    resume_skills: List[str]

class PreferenceWizard:
    def run_wizard(self) -> UserPreferences:
        """Run interactive wizard and return preferences"""
        pass
    
    def _prompt_keywords(self, prompt: str) -> List[str]:
        """Prompt for comma-separated keywords"""
        pass
    
    def _prompt_integer(self, prompt: str, default: int, min_val: int = 0) -> int:
        """Prompt for integer with validation"""
        pass
```

**Validation Rules**:
- Keywords: Split by comma, strip whitespace, convert to lowercase
- Remote preference: Must be 'yes', 'no', or 'any'
- Stipend: Non-negative integer
- Post age: Positive integer
- Max results: Positive integer, default 50
- Locations: Optional comma-separated list

### 4. Scraper Engine Module

**Purpose**: Retrieves internship listings from multiple platforms

**Interface**:
```python
@dataclass
class JobListing:
    title: str
    company: str
    stipend: Optional[int]  # In INR
    location: str
    description: str
    url: str
    posted_date: Optional[str]
    source_platform: str
    raw_stipend_text: str

class BaseScraper:
    def __init__(self, timeout: int = 10, delay: float = 1.5):
        """Initialize with timeout and delay settings"""
        pass
    
    def scrape(self, preferences: UserPreferences) -> List[JobListing]:
        """Scrape listings from platform"""
        pass
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with error handling"""
        pass
    
    def _parse_stipend(self, stipend_text: str) -> Optional[int]:
        """Parse stipend from text to integer"""
        pass

class InternshalaScr(BaseScraper):
    """Scraper for Internshala"""
    pass

class UnstopScraper(BaseScraper):
    """Scraper for Unstop"""
    pass

class NaukriScraper(BaseScraper):
    """Scraper for Naukri"""
    pass

class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn"""
    pass

class LetsInternScraper(BaseScraper):
    """Scraper for LetsIntern"""
    pass

class InternWorldScraper(BaseScraper):
    """Scraper for InternWorld"""
    pass

class ScraperEngine:
    def __init__(self, scrapers: List[BaseScraper]):
        """Initialize with list of platform scrapers"""
        pass
    
    def scrape_all(self, preferences: UserPreferences) -> List[JobListing]:
        """Scrape all platforms and aggregate results"""
        pass
```

**Implementation Details**:
- User-Agent: Rotate between common browser user agents
- Timeout: 10 seconds per request
- Delay: 1.5 seconds between requests to same domain
- Error Handling: Log failures, continue with other platforms
- Retry Logic: Single retry on timeout
- Stipend Parsing: Regex to extract numbers from text like "₹15,000/month"
- Date Parsing: Convert relative dates ("2 days ago") to absolute dates

**Scraping Strategy per Platform**:
- **Internshala**: Search page with filters, parse listing cards
- **Unstop**: Opportunities section, filter by internship type
- **Naukri**: Internship search results
- **LinkedIn**: Jobs search with internship filter
- **LetsIntern**: Browse internships page
- **InternWorld**: Internship listings page

### 5. Scoring Engine Module

**Purpose**: Calculates relevance scores for listings based on preferences

**Interface**:
```python
@dataclass
class ScoredListing:
    listing: JobListing
    score: float
    score_breakdown: Dict[str, float]

class ScoringEngine:
    def __init__(self, preferences: UserPreferences):
        """Initialize with user preferences"""
        pass
    
    def score_listing(self, listing: JobListing) -> Optional[ScoredListing]:
        """Score a single listing, return None if rejected"""
        pass
    
    def score_all(self, listings: List[JobListing]) -> List[ScoredListing]:
        """Score all listings and sort by score"""
        pass
    
    def _check_reject_keywords(self, listing: JobListing) -> bool:
        """Check if listing contains reject keywords"""
        pass
    
    def _score_keywords(self, listing: JobListing) -> float:
        """Score based on wanted keyword matches"""
        pass
    
    def _score_skills(self, listing: JobListing) -> float:
        """Score based on resume skill matches"""
        pass
    
    def _score_stipend(self, listing: JobListing) -> float:
        """Score based on stipend amount"""
        pass
    
    def _score_remote(self, listing: JobListing) -> float:
        """Score based on remote work indicators"""
        pass
    
    def _score_location(self, listing: JobListing) -> float:
        """Score based on location match"""
        pass
```

**Scoring Formula**:
```
Total Score = Keyword Score + Skill Score + Stipend Score + Remote Score + Location Score

Where:
- Keyword Score = (wanted_keyword_matches * 2)
- Skill Score = (resume_skill_matches * 1)
- Stipend Score = min((stipend - min_stipend) / 10000, 5)  # Max 5 points
- Remote Score = 5 if remote_match and user_wants_remote else 0
- Location Score = 3 if location_match else 0
```

**Remote Detection Regex**:
```python
REMOTE_PATTERNS = [
    r'\bremote\b',
    r'\bwfh\b',
    r'\bwork from home\b',
    r'\bwork-from-home\b',
    r'\bpan india\b',
    r'\bpan-india\b',
    r'\banywhere in india\b'
]
```

**Rejection Logic**:
- If any reject keyword found in title or description (case-insensitive), return None
- If stipend < min_stipend (when stipend is available), return None
- If post age > max_post_age_days, return None

### 6. Deduplicator Module

**Purpose**: Removes duplicate listings based on title and company

**Interface**:
```python
class Deduplicator:
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison"""
        pass
    
    @staticmethod
    def deduplicate(listings: List[ScoredListing]) -> List[ScoredListing]:
        """Remove duplicates, keeping highest scored version"""
        pass
    
    @staticmethod
    def _generate_key(listing: JobListing) -> str:
        """Generate unique key from title and company"""
        pass
```

**Deduplication Strategy**:
- Normalize: lowercase, strip whitespace, remove special characters
- Key: f"{normalized_title}::{normalized_company}"
- Conflict Resolution: Keep listing with highest score
- Preserve Order: Maintain sorted order after deduplication

### 7. Dashboard Generator Module

**Purpose**: Creates styled HTML dashboard with job cards

**Interface**:
```python
class DashboardGenerator:
    def __init__(self, output_dir: Path = Path("output")):
        """Initialize with output directory"""
        pass
    
    def generate(self, listings: List[ScoredListing], preferences: UserPreferences) -> Path:
        """Generate HTML dashboard and return file path"""
        pass
    
    def _generate_html(self, listings: List[ScoredListing], preferences: UserPreferences) -> str:
        """Generate HTML content"""
        pass
    
    def _generate_css(self) -> str:
        """Generate CSS styles"""
        pass
    
    def _generate_job_card(self, scored_listing: ScoredListing) -> str:
        """Generate HTML for single job card"""
        pass
    
    def _format_stipend(self, stipend: Optional[int]) -> str:
        """Format stipend for display"""
        pass
```

**HTML Structure**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>InternHunt Results</title>
    <style>/* CSS Grid layout */</style>
</head>
<body>
    <header>
        <h1>InternHunt Results</h1>
        <div class="summary">Total: X | Filtered: Y</div>
    </header>
    <main class="job-grid">
        <!-- Job cards -->
    </main>
</body>
</html>
```

**CSS Design**:
- CSS Grid: 3 columns on desktop, 2 on tablet, 1 on mobile
- Card Style: Box shadow, rounded corners, hover effects
- Color Scheme: Professional blue/gray palette
- Typography: Clean sans-serif fonts
- Responsive: Media queries for different screen sizes

**Job Card Layout**:
```html
<div class="job-card">
    <div class="score-badge">Score: 15.5</div>
    <h2 class="job-title">ML Intern</h2>
    <p class="company">TechCorp</p>
    <p class="stipend">₹20,000/month</p>
    <p class="location">Remote | Bangalore</p>
    <a href="url" target="_blank" class="apply-btn">View Details</a>
</div>
```

### 8. Browser Launcher Module

**Purpose**: Opens generated dashboard in default browser

**Interface**:
```python
class BrowserLauncher:
    @staticmethod
    def open_dashboard(file_path: Path) -> bool:
        """Open HTML file in default browser"""
        pass
```

**Implementation**:
- Use `webbrowser.open()` with file:// URL
- Return True on success, False on failure
- Fallback: Print file path if auto-open fails

### 9. Main Application Module

**Purpose**: Orchestrates the entire pipeline

**Interface**:
```python
class InternHuntApp:
    def __init__(self):
        """Initialize application components"""
        pass
    
    def run(self):
        """Execute main application flow"""
        pass
    
    def _run_resume_parser(self) -> List[str]:
        """Optional resume parsing step"""
        pass
    
    def _run_preference_wizard(self, resume_skills: List[str]) -> UserPreferences:
        """Collect user preferences"""
        pass
    
    def _run_scraping(self, preferences: UserPreferences) -> List[JobListing]:
        """Scrape all platforms"""
        pass
    
    def _run_scoring(self, listings: List[JobListing], preferences: UserPreferences) -> List[ScoredListing]:
        """Score and filter listings"""
        pass
    
    def _run_deduplication(self, listings: List[ScoredListing]) -> List[ScoredListing]:
        """Remove duplicates"""
        pass
    
    def _run_dashboard_generation(self, listings: List[ScoredListing], preferences: UserPreferences) -> Path:
        """Generate HTML dashboard"""
        pass
    
    def _run_browser_launch(self, dashboard_path: Path):
        """Open dashboard in browser"""
        pass
```

## Data Models

### Core Data Classes

```python
from dataclasses import dataclass
from typing import List, Optional, Dict
from pathlib import Path

@dataclass
class JobListing:
    """Represents a single internship listing"""
    title: str
    company: str
    stipend: Optional[int]  # In INR, None if unpaid/not specified
    location: str
    description: str
    url: str
    posted_date: Optional[str]
    source_platform: str
    raw_stipend_text: str  # Original text like "₹15,000-20,000/month"

@dataclass
class ScoredListing:
    """Job listing with calculated relevance score"""
    listing: JobListing
    score: float
    score_breakdown: Dict[str, float]  # Component scores for transparency

@dataclass
class UserPreferences:
    """User search preferences from wizard"""
    wanted_keywords: List[str]
    reject_keywords: List[str]
    remote_preference: str  # 'yes', 'no', 'any'
    min_stipend: int
    max_post_age_days: int
    max_results: int
    preferred_locations: List[str]
    resume_skills: List[str]

@dataclass
class ResumeSkills:
    """Extracted skills from resume"""
    extracted_skills: List[str]
    confidence_scores: Dict[str, float]

@dataclass
class ScrapingResult:
    """Result from scraping operation"""
    platform: str
    listings: List[JobListing]
    success: bool
    error_message: Optional[str]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Resume skill extraction bounds

*For any* valid PDF resume file, the number of extracted skills should be between 10 and 50 inclusive.

**Validates: Requirements 1.3**

### Property 2: Preference wizard input validation

*For any* user input to the preference wizard, invalid inputs (negative stipends, invalid remote preferences, non-positive post ages) should be rejected and the user should be re-prompted.

**Validates: Requirements 2.4, 2.5, 2.6, 8.3**

### Property 3: Scraper error isolation

*For any* scraping operation where one or more platforms fail, the system should continue processing remaining platforms and return all successfully scraped listings.

**Validates: Requirements 3.3, 8.2**

### Property 4: Reject keyword filtering

*For any* listing containing a reject keyword in its title or description, that listing should not appear in the final scored results regardless of its potential score.

**Validates: Requirements 4.7**

### Property 5: Wanted keyword scoring consistency

*For any* listing, the number of wanted keyword matches multiplied by 2 should equal the keyword component of the total score.

**Validates: Requirements 4.1**

### Property 6: Remote detection accuracy

*For any* listing containing remote work indicators (remote, wfh, work from home, pan india) in location or description fields, the remote detection should identify it using case-insensitive regex matching.

**Validates: Requirements 4.4, 10.1, 10.2, 10.3**

### Property 7: Stipend scoring monotonicity

*For any* two listings with stipends S1 and S2 where S1 > S2, the stipend score component for the first listing should be greater than or equal to the second listing's stipend score.

**Validates: Requirements 4.3**

### Property 8: Score-based sorting

*For any* list of scored listings, the output should be sorted in descending order by score, meaning each listing's score should be greater than or equal to the next listing's score.

**Validates: Requirements 4.8**

### Property 9: Deduplication key uniqueness

*For any* two listings with identical normalized title and company name, only one should appear in the deduplicated results.

**Validates: Requirements 5.1, 5.2**

### Property 10: Deduplication preserves highest score

*For any* set of duplicate listings, the deduplicated result should contain the listing with the highest score among the duplicates.

**Validates: Requirements 5.2**

### Property 11: HTML dashboard validity

*For any* generated dashboard, the HTML output should be valid HTML5 and contain all required elements (title, company, stipend, location, score, link) for each listing.

**Validates: Requirements 6.1, 6.2**

### Property 12: Dashboard link functionality

*For any* job card in the generated dashboard, the link should open in a new browser tab (target="_blank" attribute present).

**Validates: Requirements 6.5**

### Property 13: Stipend formatting consistency

*For any* stipend value in INR, the formatted display should include the ₹ symbol and proper thousand separators.

**Validates: Requirements 6.4**

### Property 14: Rate limiting compliance

*For any* sequence of requests to the same domain, the time between consecutive requests should be at least 1 second.

**Validates: Requirements 9.1**

### Property 15: Maximum results limit

*For any* user-specified maximum results value N, the final dashboard should contain at most N listings.

**Validates: Requirements 2.6**

## Error Handling

### Error Categories and Strategies

**1. PDF Parsing Errors**
- **Causes**: Corrupted files, encrypted PDFs, unsupported formats
- **Handling**: Log error, skip resume parsing, continue with manual skill entry
- **User Feedback**: "Unable to parse resume. Please enter skills manually."

**2. Network Errors**
- **Causes**: Timeouts, connection failures, DNS issues
- **Handling**: Single retry with exponential backoff, log failure, continue with other platforms
- **User Feedback**: "Failed to scrape [Platform]. Continuing with other sources..."

**3. Parsing Errors**
- **Causes**: Website structure changes, unexpected HTML
- **Handling**: Log error with URL, skip problematic listing, continue parsing
- **User Feedback**: Silent (logged only), don't interrupt user experience

**4. Validation Errors**
- **Causes**: Invalid user input in wizard
- **Handling**: Display error message, re-prompt for valid input
- **User Feedback**: "Invalid input. Please enter a positive number."

**5. File System Errors**
- **Causes**: Permission issues, disk full, invalid paths
- **Handling**: Display error with path, suggest alternative location
- **User Feedback**: "Cannot write to [path]. Please check permissions."

**6. Browser Launch Errors**
- **Causes**: No default browser, permission issues
- **Handling**: Print file path for manual opening
- **User Feedback**: "Dashboard saved to [path]. Please open manually."

### Logging Strategy

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('internhunt.log'),
        logging.StreamHandler()
    ]
)

# Log levels:
# ERROR: Scraping failures, parsing errors, file system errors
# WARNING: Rate limiting, missing data fields
# INFO: Progress updates, successful operations
# DEBUG: Detailed scraping data, score breakdowns
```

## Testing Strategy

### Unit Testing

**Test Coverage Areas**:

1. **Skill Matching Tests**
   - Test skill extraction with sample resume text
   - Verify similarity threshold filtering
   - Test handling of empty/invalid PDFs

2. **Preference Validation Tests**
   - Test input validation for each preference type
   - Verify default value handling
   - Test edge cases (empty strings, special characters)

3. **Stipend Parsing Tests**
   - Test various stipend formats: "₹15,000", "15000-20000", "Unpaid"
   - Verify handling of missing stipend information
   - Test range extraction (use minimum value)

4. **Scoring Logic Tests**
   - Test keyword matching with various cases
   - Verify score calculation for each component
   - Test reject keyword filtering

5. **Remote Detection Tests**
   - Test regex patterns against sample location strings
   - Verify case-insensitive matching
   - Test edge cases (partial matches, hyphenated terms)

6. **Deduplication Tests**
   - Test with exact duplicates
   - Test with case variations
   - Verify highest score retention

7. **HTML Generation Tests**
   - Verify valid HTML5 output
   - Test special character escaping
   - Verify all required fields present

### Property-Based Testing

**Framework**: Use `hypothesis` library for Python property-based testing

**Configuration**: Each property test should run minimum 100 iterations

**Test Properties**:

1. **Property Test: Skill Extraction Bounds**
   - Generate random resume text
   - Verify extracted skills count is between 10-50
   - **Feature: internhunt-v6, Property 1: Resume skill extraction bounds**

2. **Property Test: Reject Keyword Filtering**
   - Generate random listings with/without reject keywords
   - Verify listings with reject keywords are excluded
   - **Feature: internhunt-v6, Property 4: Reject keyword filtering**

3. **Property Test: Score Sorting**
   - Generate random scored listings
   - Verify output is sorted in descending order
   - **Feature: internhunt-v6, Property 8: Score-based sorting**

4. **Property Test: Deduplication Uniqueness**
   - Generate listings with duplicate title/company pairs
   - Verify each unique pair appears only once
   - **Feature: internhunt-v6, Property 9: Deduplication key uniqueness**

5. **Property Test: Stipend Scoring Monotonicity**
   - Generate listings with various stipend values
   - Verify higher stipends receive higher or equal scores
   - **Feature: internhunt-v6, Property 7: Stipend scoring monotonicity**

6. **Property Test: Rate Limiting**
   - Generate sequence of requests
   - Verify minimum delay between requests to same domain
   - **Feature: internhunt-v6, Property 14: Rate limiting compliance**

7. **Property Test: Maximum Results Limit**
   - Generate more listings than max_results
   - Verify output contains at most max_results listings
   - **Feature: internhunt-v6, Property 15: Maximum results limit**

### Integration Testing

- Test complete pipeline with mock scrapers
- Verify data flow between components
- Test error propagation and recovery

### Manual Testing Checklist

- Run with real resume PDF
- Test each platform scraper individually
- Verify dashboard renders correctly in multiple browsers
- Test with various preference combinations
- Verify ethical scraping (check request timing)

## Dependencies

### Required Libraries

```python
# requirements.txt
requests>=2.31.0
beautifulsoup4>=4.12.0
pypdf>=3.17.0
sentence-transformers>=2.2.0
numpy>=1.24.0
hypothesis>=6.92.0  # For property-based testing
```

### Standard Library Modules

- `dataclasses`: Data models
- `re`: Regex for parsing and matching
- `webbrowser`: Browser launching
- `time`: Rate limiting delays
- `pathlib`: File path handling
- `logging`: Error and info logging
- `typing`: Type hints
- `json`: Configuration handling (if needed)

## Performance Considerations

### Optimization Strategies

1. **Parallel Scraping**: Use `concurrent.futures.ThreadPoolExecutor` to scrape platforms in parallel
2. **Caching**: Cache SentenceTransformer model after first load
3. **Lazy Loading**: Load embeddings only if resume parsing is requested
4. **Batch Processing**: Process listings in batches for scoring
5. **Early Filtering**: Apply reject keywords before scoring to reduce computation

### Expected Performance

- Resume parsing: 2-5 seconds
- Scraping (6 platforms): 15-30 seconds (with rate limiting)
- Scoring: <1 second for 100 listings
- Dashboard generation: <1 second
- Total runtime: 20-40 seconds

## Security Considerations

1. **Input Sanitization**: Escape HTML special characters in user input before dashboard generation
2. **Path Traversal**: Validate file paths to prevent directory traversal attacks
3. **Request Headers**: Use realistic User-Agent to avoid being flagged as bot
4. **Rate Limiting**: Respect platform resources to avoid IP bans
5. **HTTPS**: Use HTTPS for all requests when available
6. **No Credentials**: Don't store or transmit user credentials

## Future Enhancements

1. **Database Storage**: Store listings in SQLite for historical tracking
2. **Email Notifications**: Send daily digest of new matching internships
3. **Advanced Filters**: Company size, industry, duration filters
4. **Application Tracking**: Track applied positions
5. **Salary Trends**: Analyze stipend trends over time
6. **API Mode**: Expose functionality via REST API
7. **GUI**: Desktop or web interface
8. **More Platforms**: Add international platforms (Indeed, Glassdoor)
