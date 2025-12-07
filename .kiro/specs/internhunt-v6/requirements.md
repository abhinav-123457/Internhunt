# Requirements Document

## Introduction

InternHunt v6 is a Python CLI application designed to automate the process of discovering relevant internship opportunities across multiple Indian job platforms. The system extracts skills from a user's resume, collects user preferences through an interactive wizard, scrapes internship listings from various sources, scores and ranks opportunities based on relevance, and presents results in an interactive HTML dashboard.

## Glossary

- **InternHunt System**: The complete Python CLI application that automates internship discovery
- **Resume Parser**: Component that extracts skills from PDF resumes using SentenceTransformer embeddings
- **Preference Wizard**: Interactive CLI interface for collecting user search preferences
- **Scraper Engine**: Component that retrieves internship listings from multiple job platforms
- **Scoring Engine**: Component that calculates relevance scores for internship listings
- **Dashboard Generator**: Component that creates styled HTML output with ranked results
- **Skill Library**: Predefined collection of 50+ technical and professional skills
- **Job Listing**: A single internship opportunity with metadata (title, company, stipend, location, etc.)
- **Wanted Keywords**: User-specified terms that increase listing relevance scores
- **Reject Keywords**: User-specified terms that disqualify listings from results

## Requirements

### Requirement 1

**User Story:** As a job seeker, I want to extract skills from my resume PDF, so that the system can automatically identify my qualifications for matching internships.

#### Acceptance Criteria

1. WHEN a user provides a valid PDF resume file THEN the InternHunt System SHALL extract text content from all pages
2. WHEN the Resume Parser processes extracted text THEN the InternHunt System SHALL use SentenceTransformer embeddings to identify skills from the Skill Library
3. WHEN skill matching is performed THEN the InternHunt System SHALL return a minimum of 10 and maximum of 50 matched skills
4. IF a resume file is corrupted or unreadable THEN the InternHunt System SHALL log an error message and continue with manual skill entry
5. WHERE the user chooses to skip resume upload THEN the InternHunt System SHALL proceed directly to the Preference Wizard

### Requirement 2

**User Story:** As a job seeker, I want to specify my search preferences through an interactive wizard, so that I can customize internship filtering criteria.

#### Acceptance Criteria

1. WHEN the Preference Wizard starts THEN the InternHunt System SHALL prompt the user for wanted keywords as comma-separated values
2. WHEN the Preference Wizard collects reject keywords THEN the InternHunt System SHALL prompt the user for reject keywords as comma-separated values
3. WHEN the Preference Wizard requests remote preference THEN the InternHunt System SHALL accept yes, no, or any as valid inputs
4. WHEN the Preference Wizard requests minimum stipend THEN the InternHunt System SHALL accept non-negative integer values in Indian Rupees
5. WHEN the Preference Wizard requests maximum post age THEN the InternHunt System SHALL accept positive integer values representing days
6. WHEN the Preference Wizard requests maximum results THEN the InternHunt System SHALL accept positive integer values with a default of 50
7. WHEN the Preference Wizard requests preferred locations THEN the InternHunt System SHALL accept comma-separated city names or allow empty input for any location

### Requirement 3

**User Story:** As a job seeker, I want the system to scrape internship listings from multiple Indian platforms, so that I can access opportunities from diverse sources in one place.

#### Acceptance Criteria

1. WHEN the Scraper Engine executes THEN the InternHunt System SHALL retrieve listings from Internshala, Unstop, Naukri, LinkedIn, LetsIntern, and InternWorld
2. WHEN the Scraper Engine sends HTTP requests THEN the InternHunt System SHALL include appropriate User-Agent headers to simulate browser behavior
3. WHEN the Scraper Engine encounters network errors THEN the InternHunt System SHALL log the error and continue with remaining platforms
4. WHEN the Scraper Engine processes responses THEN the InternHunt System SHALL parse title, company, stipend, location, posting date, and URL for each listing
5. WHEN the Scraper Engine makes requests THEN the InternHunt System SHALL implement delays between requests to prevent server overload
6. WHEN the Scraper Engine completes THEN the InternHunt System SHALL return all successfully scraped listings as structured data

### Requirement 4

**User Story:** As a job seeker, I want listings to be scored based on my preferences, so that the most relevant opportunities appear first.

#### Acceptance Criteria

1. WHEN the Scoring Engine evaluates a listing THEN the InternHunt System SHALL assign 2 points for each wanted keyword match in title or description
2. WHEN the Scoring Engine evaluates a listing THEN the InternHunt System SHALL assign 1 point for each skill match from the resume
3. WHEN the Scoring Engine evaluates stipend THEN the InternHunt System SHALL add bonus points proportional to stipend amount above minimum threshold
4. WHEN the Scoring Engine detects remote work indicators THEN the InternHunt System SHALL use regex patterns to identify terms like remote, wfh, work from home, and pan india
5. WHERE the user prefers remote work WHEN the Scoring Engine finds remote indicators THEN the InternHunt System SHALL add 5 bonus points
6. WHEN the Scoring Engine evaluates location THEN the InternHunt System SHALL add 3 bonus points for matches with user-preferred locations
7. IF a listing contains any reject keyword THEN the InternHunt System SHALL exclude the listing from results regardless of score
8. WHEN the Scoring Engine completes THEN the InternHunt System SHALL sort all listings by score in descending order

### Requirement 5

**User Story:** As a job seeker, I want duplicate listings to be removed, so that I see each unique opportunity only once.

#### Acceptance Criteria

1. WHEN the InternHunt System processes scraped listings THEN the InternHunt System SHALL identify duplicates by comparing normalized title and company name combinations
2. WHEN the InternHunt System detects duplicate listings THEN the InternHunt System SHALL retain the listing with the highest score
3. WHEN the InternHunt System normalizes text for comparison THEN the InternHunt System SHALL convert to lowercase and remove extra whitespace
4. WHEN deduplication completes THEN the InternHunt System SHALL maintain the sorted order of remaining unique listings

### Requirement 6

**User Story:** As a job seeker, I want results displayed in a styled HTML dashboard, so that I can easily browse and access opportunities.

#### Acceptance Criteria

1. WHEN the Dashboard Generator creates output THEN the InternHunt System SHALL generate a valid HTML5 document with embedded CSS
2. WHEN the Dashboard Generator renders listings THEN the InternHunt System SHALL display each listing as a card showing title, company, stipend, location, relevance score, and clickable link
3. WHEN the Dashboard Generator applies styling THEN the InternHunt System SHALL use CSS Grid layout for responsive card arrangement
4. WHEN the Dashboard Generator formats stipend THEN the InternHunt System SHALL display amounts in Indian Rupees with proper formatting
5. WHEN the Dashboard Generator includes links THEN the InternHunt System SHALL ensure all URLs open in new browser tabs
6. WHEN the Dashboard Generator completes THEN the InternHunt System SHALL save the HTML file to the local filesystem with a timestamped filename

### Requirement 7

**User Story:** As a job seeker, I want the dashboard to open automatically in my browser, so that I can immediately view results without manual navigation.

#### Acceptance Criteria

1. WHEN the InternHunt System generates the HTML dashboard THEN the InternHunt System SHALL automatically open the file in the default system browser
2. IF browser auto-open fails THEN the InternHunt System SHALL display the file path to the user for manual opening
3. WHEN the InternHunt System completes execution THEN the InternHunt System SHALL print a summary showing total listings found, listings after filtering, and output file location

### Requirement 8

**User Story:** As a developer, I want the system to handle errors gracefully, so that partial failures do not crash the entire application.

#### Acceptance Criteria

1. WHEN the InternHunt System encounters a PDF parsing error THEN the InternHunt System SHALL log the error and continue with manual skill entry
2. WHEN the Scraper Engine fails to access a platform THEN the InternHunt System SHALL log the failure and continue scraping remaining platforms
3. WHEN the InternHunt System encounters invalid user input THEN the InternHunt System SHALL display an error message and re-prompt for valid input
4. WHEN the InternHunt System encounters network timeouts THEN the InternHunt System SHALL retry the request once before logging failure
5. WHEN the Dashboard Generator cannot write to disk THEN the InternHunt System SHALL display an error message with the attempted file path

### Requirement 9

**User Story:** As a responsible developer, I want the scraper to follow ethical practices, so that the system does not harm target platforms or violate terms of service.

#### Acceptance Criteria

1. WHEN the Scraper Engine makes consecutive requests THEN the InternHunt System SHALL implement a minimum delay of 1 second between requests to the same domain
2. WHEN the Scraper Engine sets request parameters THEN the InternHunt System SHALL include timeout values to prevent indefinite hanging
3. WHEN the InternHunt System executes THEN the InternHunt System SHALL limit total requests per platform to prevent excessive load
4. WHEN the Scraper Engine encounters rate limiting responses THEN the InternHunt System SHALL respect the limitation and skip further requests to that platform

### Requirement 10

**User Story:** As a user focused on Indian opportunities, I want the system to recognize India-specific remote work terminology, so that remote positions are accurately identified.

#### Acceptance Criteria

1. WHEN the Scoring Engine searches for remote indicators THEN the InternHunt System SHALL use regex patterns to match remote, wfh, work from home, work-from-home, pan india, and pan-india
2. WHEN the Scoring Engine performs pattern matching THEN the InternHunt System SHALL use case-insensitive comparison
3. WHEN the Scoring Engine evaluates location fields THEN the InternHunt System SHALL check both location and description fields for remote indicators
