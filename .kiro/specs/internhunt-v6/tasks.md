# Implementation Plan

- [x] 1. Set up project structure and skill library





  - Create directory structure: `src/`, `tests/`, `output/`
  - Create `src/skill_library.py` with 50+ predefined skills organized by category
  - Create `requirements.txt` with all dependencies
  - Set up logging configuration
  - _Requirements: All requirements depend on this foundation_


- [x] 2. Implement resume parser module




  - Create `src/resume_parser.py` with ResumeParser class
  - Implement PDF text extraction using pypdf
  - Implement skill matching using SentenceTransformer embeddings
  - Handle corrupted/invalid PDF files gracefully
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2.1 Write property test for resume skill extraction bounds


  - **Property 1: Resume skill extraction bounds**
  - **Validates: Requirements 1.3**

- [x] 3. Implement preference wizard module





  - Create `src/preference_wizard.py` with PreferenceWizard class
  - Implement interactive prompts for all preference types
  - Add input validation for each preference field
  - Handle default values appropriately
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

- [x] 3.1 Write property test for preference wizard input validation


  - **Property 2: Preference wizard input validation**
  - **Validates: Requirements 2.4, 2.5, 2.6, 8.3**

- [x] 3.2 Write unit tests for preference wizard


  - Test keyword parsing (comma-separated values)
  - Test default value handling
  - Test empty input handling for optional fields
  - _Requirements: 2.1, 2.2, 2.7_

- [x] 4. Implement base scraper infrastructure





  - Create `src/scrapers/base_scraper.py` with BaseScraper class
  - Implement HTTP request handling with User-Agent rotation
  - Implement rate limiting with configurable delays
  - Implement timeout and retry logic
  - Implement stipend parsing with regex
  - _Requirements: 3.2, 3.5, 9.1, 9.2_

- [x] 4.1 Write property test for rate limiting compliance

  - **Property 14: Rate limiting compliance**
  - **Validates: Requirements 9.1**

- [x] 4.2 Write unit tests for stipend parsing

  - Test various formats: "₹15,000", "15000-20000", "Unpaid"
  - Test range extraction (minimum value)
  - Test missing stipend handling
  - _Requirements: 3.4_

- [x] 5. Implement platform-specific scrapers




  - Create `src/scrapers/internshala_scraper.py`
  - Create `src/scrapers/unstop_scraper.py`
  - Create `src/scrapers/naukri_scraper.py`
  - Create `src/scrapers/linkedin_scraper.py`
  - Create `src/scrapers/letsintern_scraper.py`
  - Create `src/scrapers/internworld_scraper.py`
  - Each scraper should parse: title, company, stipend, location, description, URL, posted_date
  - _Requirements: 3.1, 3.4_

- [x] 5.1 Write unit tests for individual scrapers

  - Create mock HTML responses for each platform
  - Test parsing of all required fields
  - Test handling of missing fields
  - _Requirements: 3.4_

- [x] 6. Implement scraper engine orchestrator





  - Create `src/scraper_engine.py` with ScraperEngine class
  - Implement parallel scraping using ThreadPoolExecutor
  - Implement error isolation (continue on individual platform failures)
  - Aggregate results from all platforms
  - _Requirements: 3.3, 3.6, 8.2_

- [x] 6.1 Write property test for scraper error isolation


  - **Property 3: Scraper error isolation**
  - **Validates: Requirements 3.3, 8.2**

- [x] 7. Implement scoring engine module





  - Create `src/scoring_engine.py` with ScoringEngine class
  - Implement keyword scoring (2 points per wanted keyword match)
  - Implement skill scoring (1 point per resume skill match)
  - Implement stipend scoring (proportional bonus)
  - Implement remote detection with regex patterns
  - Implement location matching
  - Implement reject keyword filtering
  - Sort results by score in descending order
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 10.1, 10.2, 10.3_

- [x] 7.1 Write property test for reject keyword filtering


  - **Property 4: Reject keyword filtering**
  - **Validates: Requirements 4.7**

- [x] 7.2 Write property test for wanted keyword scoring consistency

  - **Property 5: Wanted keyword scoring consistency**
  - **Validates: Requirements 4.1**

- [x] 7.3 Write property test for remote detection accuracy

  - **Property 6: Remote detection accuracy**
  - **Validates: Requirements 4.4, 10.1, 10.2, 10.3**

- [x] 7.4 Write property test for stipend scoring monotonicity

  - **Property 7: Stipend scoring monotonicity**
  - **Validates: Requirements 4.3**

- [x] 7.5 Write property test for score-based sorting

  - **Property 8: Score-based sorting**
  - **Validates: Requirements 4.8**

- [x] 7.6 Write unit tests for scoring components


  - Test keyword matching with various cases
  - Test skill matching
  - Test location matching
  - Test score calculation edge cases
  - _Requirements: 4.1, 4.2, 4.6_

- [x] 8. Implement deduplicator module





  - Create `src/deduplicator.py` with Deduplicator class
  - Implement text normalization (lowercase, strip whitespace)
  - Implement duplicate detection by title+company key
  - Retain highest scored duplicate
  - Maintain sorted order after deduplication
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 8.1 Write property test for deduplication key uniqueness


  - **Property 9: Deduplication key uniqueness**
  - **Validates: Requirements 5.1, 5.2**

- [x] 8.2 Write property test for deduplication preserves highest score


  - **Property 10: Deduplication preserves highest score**
  - **Validates: Requirements 5.2**

- [x] 8.3 Write unit tests for deduplicator


  - Test with exact duplicates
  - Test with case variations
  - Test with whitespace variations
  - Test order preservation
  - _Requirements: 5.3, 5.4_

- [x] 9. Implement dashboard generator module





  - Create `src/dashboard_generator.py` with DashboardGenerator class
  - Implement HTML5 template generation
  - Implement CSS Grid styling with responsive design
  - Implement job card rendering with all required fields
  - Implement stipend formatting with ₹ symbol and separators
  - Ensure links open in new tabs (target="_blank")
  - Generate timestamped filename
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 9.1 Write property test for HTML dashboard validity


  - **Property 11: HTML dashboard validity**
  - **Validates: Requirements 6.1, 6.2**

- [x] 9.2 Write property test for dashboard link functionality


  - **Property 12: Dashboard link functionality**
  - **Validates: Requirements 6.5**

- [x] 9.3 Write property test for stipend formatting consistency


  - **Property 13: Stipend formatting consistency**
  - **Validates: Requirements 6.4**

- [x] 9.4 Write unit tests for dashboard generator


  - Test HTML structure
  - Test special character escaping
  - Test empty results handling
  - Test CSS inclusion
  - _Requirements: 6.1, 6.3_

- [x] 10. Implement browser launcher module





  - Create `src/browser_launcher.py` with BrowserLauncher class
  - Implement auto-open using webbrowser module
  - Handle failures gracefully with fallback message
  - _Requirements: 7.1, 7.2_

- [x] 10.1 Write unit tests for browser launcher


  - Test successful browser launch
  - Test failure handling
  - _Requirements: 7.1, 7.2_

- [x] 11. Implement main application orchestrator





  - Create `src/main.py` with InternHuntApp class
  - Implement complete pipeline orchestration
  - Add optional resume parsing step
  - Integrate all modules in sequence
  - Implement max results limiting
  - Print execution summary
  - _Requirements: 1.5, 7.3_

- [ ]* 11.1 Write property test for maximum results limit
  - **Property 15: Maximum results limit**
  - **Validates: Requirements 2.6**

- [x] 12. Create CLI entry point








  - Create `internhunt.py` as main entry point
  - Add command-line argument parsing (optional: resume path)
  - Add help text and usage instructions
  - Handle keyboard interrupts gracefully
  - _Requirements: All requirements_

- [x] 13. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 14. Create integration tests
  - Test complete pipeline with mock scrapers
  - Test error propagation and recovery
  - Test data flow between components
  - _Requirements: All requirements_

- [x] 15. Add documentation and examples




  - Create README.md with installation and usage instructions
  - Add docstrings to all classes and methods
  - Create example resume PDF for testing
  - Document ethical scraping practices
  - _Requirements: All requirements_

- [x] 16. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
