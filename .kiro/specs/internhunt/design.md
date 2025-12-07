# InternHunt – Design

## Overview

InternHunt is a Python CLI application that automates internship discovery and ranking. The system collects user preferences through an interactive wizard, optionally extracts skills from a resume PDF using local ML models, scrapes internship listings from multiple sources (Internshala and Unstop), scores matches based on relevance, and generates a dark-mode HTML dashboard. All processing occurs locally to ensure privacy and offline capability (except for web scraping).

**Key Design Decisions:**
- Single-file architecture (`internhunt.py`) for simplicity and ease of distribution
- Local-only processing using sentence-transformers for skill extraction (no external APIs)
- Graceful degradation: failures on one source don't block results from others
- Dark-mode HTML dashboard for better user experience during late-night job hunting

## Architecture

The system follows a pipeline architecture with five sequential stages:

1. **Resume Ingestion (Optional)**: Extract skills from user's PDF resume
2. **Preference Collection**: Interactive wizard gathers user criteria
3. **Multi-Source Scraping**: Parallel retrieval from Internshala and Unstop
4. **Scoring & Ranking**: Calculate match scores and sort by relevance
5. **Dashboard Generation**: Create and auto-open HTML output

**Rationale**: Pipeline architecture ensures clear separation of concerns and makes it easy to add new scraping sources or scoring criteria in the future.

## Components and Interfaces

### 1. Preference Wizard Component

**Purpose**: Collect user preferences through interactive CLI prompts

**Interface**:
```python
def run_preference_wizard() -> UserPrefs:
    """
    Prompts user for preferences and returns populated UserPrefs object.
    
    Collects:
    - Role keywords (e.g., "software", "data science")
    - Location preferences (cities or "Any")
    - Remote work preference (yes/no)
    - Minimum stipend requirement (integer)
    - Maximum results to display
    
    Returns:
        UserPrefs: Dataclass containing all user preferences
    """
```

**Validates**: Requirements 1.1-1.5

### 2. Resume Parser Component

**Purpose**: Extract skills from PDF resume using local ML model

**Interface**:
```python
def extract_resume_text(pdf_path: str) -> str:
    """
    Extract raw text from PDF resume using pypdf library.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        str: Extracted text content
        
    Raises:
        FileNotFoundError: If PDF path is invalid
        ValueError: If PDF cannot be parsed
    """

def extract_keywords_from_resume(resume_text: str, top_n: int = 10) -> list[str]:
    """
    Use local sentence-transformer model to identify top skills from resume text.
    
    Uses a predefined skill taxonomy and semantic similarity to rank skills.
    Model: sentence-transformers/all-MiniLM-L6-v2 (lightweight, runs locally)
    
    Args:
        resume_text: Raw text extracted from resume
        top_n: Number of top skills to return
        
    Returns:
        list[str]: Top N relevant skills identified
    """
```

**Rationale**: Using sentence-transformers allows semantic matching without external APIs. The all-MiniLM-L6-v2 model is chosen for its balance of accuracy and speed on consumer hardware.

**Validates**: Requirements 2.1-2.5, 7.1

### 3. Scraper Components

**Purpose**: Retrieve internship listings from external websites

**Interface**:
```python
def scrape_internshala(prefs: UserPrefs) -> tuple[list[dict], str | None]:
    """
    Scrape internship listings from Internshala with engineering/software filters.
    
    Args:
        prefs: User preferences for filtering
        
    Returns:
        tuple: (list of internship dicts, error message if failed)
        
    Error Handling:
        - Network errors: return ([], error_msg)
        - Parsing errors on individual listings: skip and continue
        - Complete failure: return ([], error_msg)
    """

def scrape_unstop(prefs: UserPrefs) -> tuple[list[dict], str | None]:
    """
    Scrape internship listings from Unstop internships page.
    
    Args:
        prefs: User preferences for filtering
        
    Returns:
        tuple: (list of internship dicts, error message if failed)
        
    Error Handling:
        - Network errors: return ([], error_msg)
        - Parsing errors on individual listings: skip and continue
        - Complete failure: return ([], error_msg)
    """
```

**Rationale**: Each scraper returns both results and error status, allowing the main pipeline to continue even if one source fails. This satisfies the graceful degradation requirement.

**Validates**: Requirements 3.1-3.6, 4.1-4.6, 8.1-8.5

### 4. Scoring Engine Component

**Purpose**: Calculate match scores based on user preferences and skills

**Interface**:
```python
def match_score(prefs: UserPrefs, internship: dict) -> float:
    """
    Calculate match score for an internship based on multiple criteria.
    
    Scoring algorithm:
    - Role keyword match: +10 points per matching keyword in title/description
    - Location match: +20 points if location matches preference
    - Remote match: +15 points if remote and user wants remote
    - Stipend: +5 points per 1000 above minimum requirement
    - Resume skill match: +8 points per matching skill (if resume provided)
    
    Args:
        prefs: User preferences including keywords and resume skills
        internship: Internship dict with title, location, stipend, etc.
        
    Returns:
        float: Total match score (higher is better)
    """

def parse_stipend_number(stipend_str: str) -> int:
    """Convert stipend text like '₹15,000/month' to integer 15000."""

def text_age_to_days(text: str) -> int:
    """Convert posting age like '3 days ago' to integer days."""
```

**Rationale**: Weighted scoring system prioritizes location and remote preferences (higher weights) while still considering keywords and stipend. Resume skills receive moderate weight to balance automated extraction with explicit preferences.

**Validates**: Requirements 5.1-5.6

### 5. Dashboard Generator Component

**Purpose**: Generate dark-mode HTML dashboard with ranked internships

**Interface**:
```python
def render_dashboard(prefs: UserPrefs, listings: list[dict]) -> str:
    """
    Generate dark-mode HTML dashboard with internship cards.
    
    Layout:
    - Header with user preferences summary
    - Grid of internship cards (responsive, 1-3 columns)
    - Each card shows: title, company, location, stipend, score, link
    - Cards ordered by descending match score
    - Dark background (#1a1a1a) with light text (#e0e0e0)
    
    Args:
        prefs: User preferences for display in header
        listings: Sorted list of internship dicts with scores
        
    Returns:
        str: Complete HTML document
    """

def open_dashboard(html_path: str) -> None:
    """Open HTML file in default browser using webbrowser module."""
```

**Rationale**: Dark mode reduces eye strain during extended browsing sessions. Card layout provides clear visual separation and makes it easy to scan multiple opportunities quickly.

**Validates**: Requirements 6.1-6.5

## Data Models

### UserPrefs Dataclass

```python
@dataclass
class UserPrefs:
    """User preferences collected from wizard and resume."""
    role_keywords: list[str]          # Keywords for role matching
    resume_skills: list[str]          # Skills extracted from resume (empty if no resume)
    locations: list[str]              # Preferred locations or ["Any"]
    remote_ok: bool                   # Whether remote work is acceptable
    min_stipend: int                  # Minimum stipend in local currency
    max_results: int                  # Maximum internships to display
    reject_keywords: list[str]        # Keywords to filter out (optional)
```

### Internship Dict

```python
{
    "source": str,        # "Internshala" or "Unstop"
    "title": str,         # Job title
    "company": str,       # Company name
    "stipend": str,       # Original stipend text (e.g., "₹15,000/month")
    "location": str,      # Location text (e.g., "Bangalore" or "Remote")
    "link": str,          # Application URL
    "score": float,       # Calculated match score
    "posted": str,        # Human-readable posting age or deadline
}
```

**Rationale**: Using a dataclass for UserPrefs provides type safety and clear documentation. Internship dict is kept simple for easy JSON serialization if needed in future versions.

## Control Flow

```
START
  ↓
[Ask: Use resume?]
  ↓
  ├─ Yes → [Extract PDF text] → [Extract skills via ML model]
  │                                      ↓
  └─ No ─────────────────────────────────┘
  ↓
[Run Preference Wizard] → UserPrefs
  ↓
[Merge resume_skills into UserPrefs]
  ↓
[Scrape Internshala] ──┐
[Scrape Unstop]     ───┤→ [Combine results + error summary]
  ↓
[Calculate match scores for each internship]
  ↓
[Sort by (score DESC, stipend DESC)]
  ↓
[Keep top max_results internships]
  ↓
[Generate internhunt_dashboard.html]
  ↓
[Open in default browser]
  ↓
END
```

**Error Handling Flow**:
- If Internshala fails: continue with Unstop results only
- If Unstop fails: continue with Internshala results only
- If both fail: display error and exit gracefully
- If individual listing fails to parse: skip and continue with others

**Validates**: Requirements 8.1-8.5

## Error Handling

### Resume Processing Errors
- **Invalid PDF path**: Display error, skip resume processing, continue with wizard
- **PDF parsing failure**: Display warning, skip resume processing, continue with wizard
- **ML model loading failure**: Display error, skip resume processing, continue with wizard

### Scraping Errors
- **Network timeout**: Log error, return empty results for that source, continue
- **HTML parsing error on listing**: Skip that listing, continue with others
- **Complete source failure**: Log error, display summary, continue with other sources
- **All sources fail**: Display comprehensive error message, exit gracefully

### Dashboard Generation Errors
- **File write permission error**: Display error with path, suggest alternative location
- **Browser open failure**: Display success message with file path for manual opening

**Rationale**: Graceful degradation ensures users get partial results rather than complete failure. Clear error messages help users understand what went wrong and what data is available.

**Validates**: Requirements 8.1-8.5

## Testing Strategy

### Unit Tests
- Test `parse_stipend_number` with various formats: "₹15,000", "15000/month", "Unpaid"
- Test `text_age_to_days` with various formats: "3 days ago", "1 week ago", "Posted today"
- Test `match_score` with known inputs and expected scores
- Test resume text extraction with sample PDF
- Test HTML generation produces valid HTML structure

### Property-Based Tests
Properties will be defined after prework analysis in the Correctness Properties section below.

### Integration Tests
- End-to-end test with mock scrapers returning known data
- Test error handling with simulated network failures
- Test dashboard generation and file creation

### Manual Testing
- Test on Linux and Windows with Python 3.10+
- Test with real resume PDFs of varying formats
- Test with actual Internshala and Unstop websites
- Verify dark-mode rendering in multiple browsers

**Testing Framework**: pytest for unit and property-based tests, pytest-mock for mocking scrapers

**Rationale**: Combination of unit tests (specific examples), property tests (universal behaviors), and integration tests (end-to-end flows) provides comprehensive coverage. Manual testing ensures real-world compatibility.

**Validates**: Requirements 7.4-7.5


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies:
- Requirements 3.2-3.6 and 4.2-4.6 test the same extraction behavior for two different sources. These can be combined into a single property about scraper extraction completeness.
- Requirements 5.1-5.5 all test different aspects of the scoring algorithm. These can be combined into a comprehensive scoring property.
- Requirements 8.1 and 8.2 test the same error handling pattern for different sources. These can be combined into one property about graceful degradation.

### Properties

**Property 1: PDF text extraction succeeds for valid PDFs**
*For any* valid PDF file, the `extract_resume_text` function should return non-empty text content without raising exceptions.
**Validates: Requirements 2.2**

**Property 2: Skill extraction returns valid skills**
*For any* non-empty resume text, the `extract_keywords_from_resume` function should return a list of skills with length between 0 and top_n (inclusive).
**Validates: Requirements 2.3**

**Property 3: Extracted skills are incorporated into preferences**
*For any* set of extracted skills and UserPrefs object, merging the skills should result in those skills appearing in the final UserPrefs.resume_skills field.
**Validates: Requirements 2.4**

**Property 4: Scraper extraction completeness**
*For any* valid internship listing HTML (from either Internshala or Unstop), the scraper should extract all required fields: title, company, location, stipend, and link. Each field should be non-empty or have a default value.
**Validates: Requirements 3.2-3.6, 4.2-4.6**

**Property 5: Scoring reflects all preference criteria**
*For any* internship and UserPrefs, the match score should:
- Increase when role keywords match the title/description
- Increase when location matches preferences
- Increase when remote matches user's remote preference
- Increase when stipend exceeds minimum requirement
- Increase when resume skills match (if resume provided)
**Validates: Requirements 5.1-5.5**

**Property 6: Ranking maintains descending score order**
*For any* list of scored internships, after sorting by the ranking algorithm, each internship's score should be greater than or equal to the next internship's score.
**Validates: Requirements 5.6**

**Property 7: Dashboard HTML contains dark-mode styling**
*For any* generated dashboard HTML, the document should contain dark background colors (e.g., #1a1a1a or similar dark hex values) in the CSS styling.
**Validates: Requirements 6.2**

**Property 8: Dashboard cards contain all required fields**
*For any* internship in the dashboard HTML, the rendered card should contain text matching the internship's title, company, location, stipend, score, and a link element with the application URL.
**Validates: Requirements 6.3**

**Property 9: Dashboard maintains score ordering**
*For any* list of internships rendered in the dashboard HTML, the visual order of cards should match the descending score order of the input list.
**Validates: Requirements 6.4**

**Property 10: Graceful degradation on source failure**
*For any* scraping operation where one source fails (returns empty results with error), the system should continue and return results from the other source without raising exceptions.
**Validates: Requirements 8.1, 8.2**

**Property 11: Individual listing failures don't block batch**
*For any* batch of listings where some fail to parse, the scraper should return successfully parsed listings and skip the failed ones without raising exceptions.
**Validates: Requirements 8.3**

**Property 12: Error summary reflects actual failures**
*For any* combination of scraping successes and failures, the error summary should accurately report which sources succeeded and which failed.
**Validates: Requirements 8.4**
