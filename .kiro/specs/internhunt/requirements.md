# Requirements Document

## Introduction

InternHunt is a Python CLI tool that automates the process of finding and ranking internship opportunities from multiple sources. The system collects user preferences, optionally extracts skills from a resume, scrapes internship listings from Internshala and Unstop, scores matches based on relevance, and generates an HTML dashboard for easy review. All processing occurs locally without external APIs or cloud services.

## Glossary

- **InternHunt System**: The Python CLI application that collects preferences, scrapes internships, scores matches, and generates output
- **User**: A student or job seeker looking for internship opportunities
- **Preference Wizard**: The interactive CLI component that collects user input about desired roles, locations, remote work, and stipend
- **Resume Parser**: The component that extracts skills from a PDF resume using a local sentence-transformer model
- **Scraper**: The component that retrieves internship listings from external websites
- **Scoring Engine**: The component that calculates match scores between user preferences and internship listings
- **Dashboard**: The HTML output file displaying ranked internship opportunities
- **Match Score**: A numerical value representing how well an internship aligns with user preferences and skills

## Requirements

### Requirement 1

**User Story:** As a user, I want to provide my internship preferences through an interactive wizard, so that the system can find relevant opportunities matching my criteria.

#### Acceptance Criteria

1. WHEN the InternHunt System starts, THE InternHunt System SHALL prompt the user for role preferences
2. WHEN the InternHunt System prompts for preferences, THE InternHunt System SHALL collect location preferences from the user
3. WHEN the InternHunt System prompts for preferences, THE InternHunt System SHALL collect remote work preferences from the user
4. WHEN the InternHunt System prompts for preferences, THE InternHunt System SHALL collect minimum stipend requirements from the user
5. WHEN the user completes the Preference Wizard, THE InternHunt System SHALL store all preferences for use in scoring

### Requirement 2

**User Story:** As a user, I want to optionally provide my resume PDF, so that the system can automatically extract my skills and improve matching accuracy.

#### Acceptance Criteria

1. WHEN the Preference Wizard runs, THE InternHunt System SHALL offer the user an option to provide a resume PDF file path
2. WHEN the user provides a resume PDF path, THE Resume Parser SHALL extract text content from the PDF file
3. WHEN the Resume Parser extracts text, THE Resume Parser SHALL use a local sentence-transformer model to identify top skills
4. WHEN the Resume Parser identifies skills, THE InternHunt System SHALL incorporate those skills into the matching criteria
5. WHEN the user declines to provide a resume, THE InternHunt System SHALL proceed with only the manually entered preferences

### Requirement 3

**User Story:** As a user, I want the system to scrape internship listings from Internshala, so that I can discover engineering and software opportunities without manual searching.

#### Acceptance Criteria

1. WHEN the InternHunt System initiates scraping, THE Scraper SHALL retrieve internship listings from Internshala with engineering and software filters applied
2. WHEN the Scraper retrieves listings, THE Scraper SHALL extract the internship title from each listing
3. WHEN the Scraper retrieves listings, THE Scraper SHALL extract the company name from each listing
4. WHEN the Scraper retrieves listings, THE Scraper SHALL extract the location information from each listing
5. WHEN the Scraper retrieves listings, THE Scraper SHALL extract the stipend information from each listing
6. WHEN the Scraper retrieves listings, THE Scraper SHALL extract the application link from each listing

### Requirement 4

**User Story:** As a user, I want the system to scrape internship listings from Unstop, so that I can access additional opportunities beyond a single source.

#### Acceptance Criteria

1. WHEN the InternHunt System initiates scraping, THE Scraper SHALL retrieve internship listings from the Unstop internships listing page
2. WHEN the Scraper retrieves Unstop listings, THE Scraper SHALL extract the internship title from each listing
3. WHEN the Scraper retrieves Unstop listings, THE Scraper SHALL extract the company name from each listing
4. WHEN the Scraper retrieves Unstop listings, THE Scraper SHALL extract the location information from each listing
5. WHEN the Scraper retrieves Unstop listings, THE Scraper SHALL extract the stipend information from each listing
6. WHEN the Scraper retrieves Unstop listings, THE Scraper SHALL extract the application link from each listing

### Requirement 5

**User Story:** As a user, I want the system to score and rank internships based on how well they match my preferences and skills, so that I can focus on the most relevant opportunities first.

#### Acceptance Criteria

1. WHEN the Scraper completes data collection, THE Scoring Engine SHALL calculate a match score for each internship based on role keyword matching
2. WHEN the Scraper completes data collection, THE Scoring Engine SHALL calculate a match score for each internship based on location preferences
3. WHEN the Scraper completes data collection, THE Scoring Engine SHALL calculate a match score for each internship based on remote work preferences
4. WHEN the Scraper completes data collection, THE Scoring Engine SHALL calculate a match score for each internship based on stipend requirements
5. WHERE a resume was provided, THE Scoring Engine SHALL incorporate skill matching into the overall match score
6. WHEN all scores are calculated, THE Scoring Engine SHALL rank internships in descending order by match score

### Requirement 6

**User Story:** As a user, I want the system to generate a dark-mode HTML dashboard with all ranked internships, so that I can easily review opportunities in a visually appealing format.

#### Acceptance Criteria

1. WHEN the Scoring Engine completes ranking, THE InternHunt System SHALL generate an HTML file named `internhunt_dashboard.html`
2. WHEN the InternHunt System generates the HTML file, THE InternHunt System SHALL apply a dark-mode color scheme to the dashboard
3. WHEN the InternHunt System generates the HTML file, THE InternHunt System SHALL create a card layout for each internship displaying title, company, location, stipend, match score, and application link
4. WHEN the InternHunt System generates the HTML file, THE InternHunt System SHALL order cards by descending match score
5. WHEN the HTML file is created, THE InternHunt System SHALL automatically open the dashboard in the default web browser

### Requirement 7

**User Story:** As a user, I want the system to run entirely on my local machine without external APIs or cloud services, so that my data remains private and the tool works offline.

#### Acceptance Criteria

1. WHEN the InternHunt System processes a resume, THE Resume Parser SHALL use a locally installed sentence-transformer model
2. WHEN the InternHunt System operates, THE InternHunt System SHALL not transmit user data to external APIs or cloud services
3. WHEN the InternHunt System operates, THE InternHunt System SHALL not require internet connectivity except for scraping public internship websites
4. THE InternHunt System SHALL run on Python 3.10 or higher on Linux operating systems
5. THE InternHunt System SHALL run on Python 3.10 or higher on Windows operating systems

### Requirement 8

**User Story:** As a user, I want the system to handle errors gracefully during scraping, so that failures on one website do not prevent me from seeing results from other sources.

#### Acceptance Criteria

1. WHEN the Scraper encounters a network error on Internshala, THE InternHunt System SHALL continue scraping from Unstop
2. WHEN the Scraper encounters a network error on Unstop, THE InternHunt System SHALL continue with results from Internshala
3. WHEN the Scraper encounters parsing errors on a specific listing, THE Scraper SHALL skip that listing and continue processing remaining listings
4. WHEN scraping completes with partial failures, THE InternHunt System SHALL display a summary of successful and failed sources
5. WHEN no internships are successfully scraped, THE InternHunt System SHALL display an error message and exit gracefully
