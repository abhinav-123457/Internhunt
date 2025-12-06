# Implementation Plan

- [ ] 1. Set up project structure and dependencies
  - Create `internhunt.py` as main entry point
  - Create `requirements.txt` with dependencies: pypdf, sentence-transformers, beautifulsoup4, requests, pytest, hypothesis
  - Set up basic project structure with imports
  - _Requirements: 7.4, 7.5_

- [ ] 2. Implement UserPrefs data model
  - Create UserPrefs dataclass with all required fields: role_keywords, resume_skills, locations, remote_ok, min_stipend, max_results, reject_keywords
  - Add type hints for all fields
  - _Requirements: 1.5_

- [ ] 3. Implement preference wizard
  - Create `run_preference_wizard()` function that prompts for role keywords
  - Add prompts for location preferences
  - Add prompt for remote work preference
  - Add prompt for minimum stipend
  - Add prompt for maximum results to display
  - Return populated UserPrefs object
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 4. Implement resume parser component
- [ ] 4.1 Create PDF text extraction function
  - Implement `extract_resume_text(pdf_path)` using pypdf library
  - Handle FileNotFoundError and ValueError exceptions
  - Return extracted text content
  - _Requirements: 2.2_

- [ ] 4.2 Write property test for PDF extraction
  - **Property 1: PDF text extraction succeeds for valid PDFs**
  - **Validates: Requirements 2.2**

- [ ] 4.3 Create skill extraction function
  - Implement `extract_keywords_from_resume(resume_text, top_n)` using sentence-transformers
  - Load all-MiniLM-L6-v2 model locally
  - Define predefined skill taxonomy for matching
  - Use semantic similarity to rank skills
  - Return top N skills
  - _Requirements: 2.3, 7.1_

- [ ] 4.4 Write property test for skill extraction
  - **Property 2: Skill extraction returns valid skills**
  - **Validates: Requirements 2.3**

- [ ] 4.5 Implement skill merging into preferences
  - Add logic to merge extracted skills into UserPrefs.resume_skills
  - _Requirements: 2.4_

- [ ] 4.6 Write property test for skill merging
  - **Property 3: Extracted skills are incorporated into preferences**
  - **Validates: Requirements 2.4**

- [ ] 4.7 Add resume prompt to main flow
  - Prompt user whether to provide resume at startup
  - If yes, call extraction functions and merge skills
  - If no, continue with empty resume_skills
  - Handle errors gracefully and continue on failure
  - _Requirements: 2.1, 2.5_

- [ ] 5. Implement scoring utilities
- [ ] 5.1 Create stipend parser
  - Implement `parse_stipend_number(stipend_str)` to convert text like "₹15,000/month" to integer
  - Handle various formats: with/without currency symbols, with/without commas
  - Handle "Unpaid" or empty stipend strings (return 0)
  - _Requirements: 5.4_

- [ ] 5.2 Write unit tests for stipend parser
  - Test various formats: "₹15,000", "15000/month", "Unpaid", empty string
  - _Requirements: 5.4_

- [ ] 5.3 Create posting age parser
  - Implement `text_age_to_days(text)` to convert "3 days ago" to integer
  - Handle formats: "N days ago", "N weeks ago", "Posted today"
  - _Requirements: 5.6_

- [ ] 5.4 Write unit tests for age parser
  - Test various formats: "3 days ago", "1 week ago", "Posted today"
  - _Requirements: 5.6_

- [ ] 5.5 Implement match scoring function
  - Create `match_score(prefs, internship)` function
  - Add role keyword matching logic (+10 points per match)
  - Add location matching logic (+20 points for match)
  - Add remote matching logic (+15 points if remote and user wants remote)
  - Add stipend scoring (+5 points per 1000 above minimum)
  - Add resume skill matching (+8 points per matching skill)
  - Return total score as float
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 5.6 Write property test for scoring
  - **Property 5: Scoring reflects all preference criteria**
  - **Validates: Requirements 5.1-5.5**

- [ ] 6. Implement Internshala scraper
- [ ] 6.1 Create scraper function
  - Implement `scrape_internshala(prefs)` function
  - Make HTTP request to Internshala with engineering/software filters
  - Parse HTML response using BeautifulSoup
  - Extract title, company, location, stipend, link, posted date from each listing
  - Return tuple of (list of internship dicts, error message or None)
  - Handle network errors gracefully (return empty list with error message)
  - Handle parsing errors on individual listings (skip and continue)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 8.1, 8.3_

- [ ] 6.2 Write property test for extraction completeness
  - **Property 4: Scraper extraction completeness** (Internshala portion)
  - **Validates: Requirements 3.2-3.6**

- [ ] 7. Implement Unstop scraper
- [ ] 7.1 Create scraper function
  - Implement `scrape_unstop(prefs)` function
  - Make HTTP request to Unstop internships page
  - Parse HTML response using BeautifulSoup
  - Extract title, company, location, stipend, link, posted date from each listing
  - Return tuple of (list of internship dicts, error message or None)
  - Handle network errors gracefully (return empty list with error message)
  - Handle parsing errors on individual listings (skip and continue)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 8.2, 8.3_

- [ ] 7.2 Write property test for extraction completeness
  - **Property 4: Scraper extraction completeness** (Unstop portion)
  - **Validates: Requirements 4.2-4.6**

- [ ] 8. Implement scraping orchestration and error handling
- [ ] 8.1 Create main scraping function
  - Call both scrapers (Internshala and Unstop)
  - Combine results from both sources
  - Track which sources succeeded and which failed
  - Generate error summary message
  - _Requirements: 8.1, 8.2, 8.4_

- [ ] 8.2 Write property test for graceful degradation
  - **Property 10: Graceful degradation on source failure**
  - **Validates: Requirements 8.1, 8.2**

- [ ] 8.3 Write property test for individual listing failures
  - **Property 11: Individual listing failures don't block batch**
  - **Validates: Requirements 8.3**

- [ ] 8.4 Write property test for error summary accuracy
  - **Property 12: Error summary reflects actual failures**
  - **Validates: Requirements 8.4**

- [ ] 8.5 Add check for zero results
  - If no internships scraped from any source, display error and exit gracefully
  - _Requirements: 8.5_

- [ ] 9. Implement ranking logic
- [ ] 9.1 Create ranking function
  - Calculate match score for each internship using `match_score()`
  - Sort internships by score descending, then by stipend descending
  - Keep top `prefs.max_results` internships
  - _Requirements: 5.6_

- [ ] 9.2 Write property test for ranking order
  - **Property 6: Ranking maintains descending score order**
  - **Validates: Requirements 5.6**

- [ ] 10. Implement dashboard generator
- [ ] 10.1 Create HTML rendering function
  - Implement `render_dashboard(prefs, listings)` function
  - Generate HTML structure with header showing user preferences
  - Create responsive grid layout (1-3 columns)
  - Apply dark-mode color scheme (background #1a1a1a, text #e0e0e0)
  - Generate card for each internship with all required fields
  - Order cards by descending match score
  - Return complete HTML document as string
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 10.2 Write property test for dark-mode styling
  - **Property 7: Dashboard HTML contains dark-mode styling**
  - **Validates: Requirements 6.2**

- [ ] 10.3 Write property test for card completeness
  - **Property 8: Dashboard cards contain all required fields**
  - **Validates: Requirements 6.3**

- [ ] 10.4 Write property test for card ordering
  - **Property 9: Dashboard maintains score ordering**
  - **Validates: Requirements 6.4**

- [ ] 10.5 Create dashboard file writer and opener
  - Write HTML to `internhunt_dashboard.html` file
  - Implement `open_dashboard(html_path)` using webbrowser module
  - Handle file write errors gracefully
  - Handle browser open failures gracefully (show file path)
  - _Requirements: 6.1, 6.5_

- [ ] 11. Integrate all components into main pipeline
- [ ] 11.1 Create main function
  - Prompt for resume (optional)
  - If resume provided, extract text and skills
  - Run preference wizard
  - Merge resume skills into preferences
  - Run scrapers and combine results
  - Display error summary if any failures
  - Exit if no results
  - Calculate scores for all internships
  - Rank and filter to top N
  - Generate dashboard HTML
  - Write to file and open in browser
  - _Requirements: All_

- [ ] 11.2 Write integration test for end-to-end flow
  - Test complete pipeline with mock scrapers
  - Verify dashboard generation with known inputs
  - _Requirements: All_

- [ ] 12. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
