"""
Main Application Module

Orchestrates the complete InternHunt pipeline from resume parsing to dashboard generation.
Integrates all modules in sequence with proper error handling and user feedback.
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

from .resume_parser import ResumeParser, ResumeSkills
from .preference_wizard import PreferenceWizard, UserPreferences
from .scraper_engine import ScraperEngine
from .scoring_engine import ScoringEngine, ScoredListing
from .deduplicator import Deduplicator
from .dashboard_generator import DashboardGenerator
from .browser_launcher import BrowserLauncher
from .logging_config import get_logger


logger = get_logger(__name__)


class InternHuntApp:
    """
    Main application orchestrator for InternHunt v6.
    
    Coordinates the complete pipeline:
    1. Resume parsing (optional)
    2. Preference collection
    3. Web scraping
    4. Scoring and filtering
    5. Deduplication
    6. Dashboard generation
    7. Browser launch
    """
    
    def __init__(self):
        """Initialize the InternHunt application."""
        logger.info("Initializing InternHunt v6")
        
        # Initialize components (lazy loading for heavy components)
        self.resume_parser: Optional[ResumeParser] = None
        self.preference_wizard = PreferenceWizard()
        self.scraper_engine: Optional[ScraperEngine] = None
        self.dashboard_generator = DashboardGenerator()
        
        logger.info("InternHunt v6 initialized successfully")
    
    def run(self, resume_path: Optional[Path] = None):
        """
        Execute the main application flow.
        
        Args:
            resume_path: Optional path to PDF resume file
        """
        try:
            logger.info("="*60)
            logger.info("Starting InternHunt v6 execution")
            logger.info("="*60)
            
            # Print welcome message
            self._print_welcome()
            
            # Step 1: Resume parsing (optional)
            resume_skills = self._run_resume_parser(resume_path)
            
            # Step 2: Preference collection
            preferences = self._run_preference_wizard(resume_skills)
            
            # Step 3: Web scraping
            raw_listings = self._run_scraping(preferences)
            
            # Check if we got any listings
            if not raw_listings:
                logger.warning("No listings found from any platform")
                print("\n⚠️  No internship listings found from any platform.")
                print("This could be due to network issues or platform changes.")
                print("Please try again later or check your internet connection.")
                return
            
            # Step 4: Scoring and filtering
            scored_listings = self._run_scoring(raw_listings, preferences)
            
            # Check if any listings passed filtering
            if not scored_listings:
                logger.warning("No listings passed filtering criteria")
                print("\n⚠️  No internships match your criteria.")
                print("Try adjusting your preferences (e.g., lower minimum stipend, fewer reject keywords).")
                return
            
            # Step 5: Deduplication
            unique_listings = self._run_deduplication(scored_listings)
            
            # Step 6: Apply max results limit
            final_listings = self._apply_max_results_limit(unique_listings, preferences.max_results)
            
            # Step 7: Dashboard generation
            dashboard_path = self._run_dashboard_generation(final_listings, preferences)
            
            # Step 8: Browser launch
            self._run_browser_launch(dashboard_path)
            
            # Step 9: Print execution summary
            self._print_summary(len(raw_listings), len(scored_listings), len(final_listings), dashboard_path)
            
            logger.info("InternHunt v6 execution completed successfully")
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            print("\n\n👋 InternHunt interrupted. Goodbye!")
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            print(f"\n❌ An error occurred: {e}")
            print("Check internhunt.log for details.")
            sys.exit(1)
    
    def _print_welcome(self):
        """Print welcome message."""
        print("\n" + "="*60)
        print("🎯 InternHunt v6 - Automated Internship Discovery")
        print("="*60)
        print("\nWelcome! Let's find your perfect internship.\n")
    
    def _run_resume_parser(self, resume_path: Optional[Path]) -> List[str]:
        """
        Optional resume parsing step.
        
        Args:
            resume_path: Path to PDF resume file (or None to skip)
            
        Returns:
            List[str]: Extracted skills or empty list
        """
        if resume_path is None:
            logger.info("Skipping resume parsing (no resume provided)")
            return []
        
        try:
            print(f"\n📄 Parsing resume: {resume_path}")
            
            # Initialize resume parser (lazy loading)
            if self.resume_parser is None:
                print("Loading AI model for skill extraction...")
                self.resume_parser = ResumeParser()
            
            # Parse resume
            result = self.resume_parser.parse_resume(resume_path)
            
            if result is None or not result.extracted_skills:
                logger.warning("Resume parsing failed or no skills extracted")
                print("⚠️  Unable to extract skills from resume. Continuing without resume skills.")
                return []
            
            print(f"✓ Extracted {len(result.extracted_skills)} skills from resume")
            logger.info(f"Extracted skills: {', '.join(result.extracted_skills[:10])}...")
            
            return result.extracted_skills
            
        except Exception as e:
            logger.error(f"Resume parsing error: {e}")
            print(f"⚠️  Resume parsing failed: {e}")
            print("Continuing without resume skills.")
            return []
    
    def _run_preference_wizard(self, resume_skills: List[str]) -> UserPreferences:
        """
        Collect user preferences through interactive wizard.
        
        Args:
            resume_skills: Skills extracted from resume
            
        Returns:
            UserPreferences: Collected preferences
        """
        logger.info("Starting preference wizard")
        preferences = self.preference_wizard.run_wizard(resume_skills)
        return preferences
    
    def _run_scraping(self, preferences: UserPreferences) -> List:
        """
        Scrape internship listings from all platforms.
        
        Args:
            preferences: User preferences
            
        Returns:
            List[JobListing]: Raw scraped listings
        """
        print("\n🔍 Scraping internship listings from multiple platforms...")
        print("This may take 20-30 seconds...\n")
        
        # Initialize scraper engine (lazy loading)
        if self.scraper_engine is None:
            self.scraper_engine = ScraperEngine()
        
        # Scrape all platforms
        listings = self.scraper_engine.scrape_all(preferences)
        
        print(f"\n✓ Scraped {len(listings)} total listings")
        
        return listings
    
    def _run_scoring(self, listings: List, preferences: UserPreferences) -> List[ScoredListing]:
        """
        Score and filter listings based on preferences.
        
        Args:
            listings: Raw job listings
            preferences: User preferences
            
        Returns:
            List[ScoredListing]: Scored and filtered listings
        """
        print("\n⚖️  Scoring and filtering listings...")
        
        # Initialize scoring engine
        scoring_engine = ScoringEngine(preferences)
        
        # Score all listings
        scored_listings = scoring_engine.score_all(listings)
        
        print(f"✓ {len(scored_listings)} listings passed filtering")
        
        return scored_listings
    
    def _run_deduplication(self, listings: List[ScoredListing]) -> List[ScoredListing]:
        """
        Remove duplicate listings.
        
        Args:
            listings: Scored listings
            
        Returns:
            List[ScoredListing]: Deduplicated listings
        """
        print("\n🔄 Removing duplicates...")
        
        # Deduplicate
        unique_listings = Deduplicator.deduplicate(listings)
        
        duplicates_removed = len(listings) - len(unique_listings)
        if duplicates_removed > 0:
            print(f"✓ Removed {duplicates_removed} duplicate(s)")
        else:
            print("✓ No duplicates found")
        
        return unique_listings
    
    def _apply_max_results_limit(self, listings: List[ScoredListing], max_results: int) -> List[ScoredListing]:
        """
        Apply maximum results limit.
        
        Args:
            listings: Deduplicated listings
            max_results: Maximum number of results to return
            
        Returns:
            List[ScoredListing]: Limited listings
        """
        if len(listings) <= max_results:
            return listings
        
        logger.info(f"Limiting results from {len(listings)} to {max_results}")
        print(f"\n📊 Limiting results to top {max_results} listings")
        
        return listings[:max_results]
    
    def _run_dashboard_generation(self, listings: List[ScoredListing], preferences: UserPreferences) -> Path:
        """
        Generate HTML dashboard.
        
        Args:
            listings: Final scored listings
            preferences: User preferences
            
        Returns:
            Path: Path to generated dashboard
        """
        print("\n📊 Generating HTML dashboard...")
        
        # Generate dashboard
        dashboard_path = self.dashboard_generator.generate(listings, preferences)
        
        print(f"✓ Dashboard generated: {dashboard_path.name}")
        
        return dashboard_path
    
    def _run_browser_launch(self, dashboard_path: Path):
        """
        Open dashboard in browser.
        
        Args:
            dashboard_path: Path to dashboard HTML file
        """
        print("\n🌐 Opening dashboard in browser...")
        
        # Try to open in browser
        success = BrowserLauncher.open_dashboard(dashboard_path)
        
        if success:
            print("✓ Dashboard opened in browser")
        else:
            # Fallback message
            print("⚠️  Could not open browser automatically")
            print(BrowserLauncher.get_fallback_message(dashboard_path))
    
    def _print_summary(self, total_scraped: int, after_filtering: int, final_count: int, dashboard_path: Path):
        """
        Print execution summary.
        
        Args:
            total_scraped: Total listings scraped
            after_filtering: Listings after filtering
            final_count: Final listing count
            dashboard_path: Path to dashboard
        """
        print("\n" + "="*60)
        print("📈 Execution Summary")
        print("="*60)
        print(f"Total listings scraped:     {total_scraped}")
        print(f"After filtering:            {after_filtering}")
        print(f"After deduplication:        {final_count}")
        print(f"Dashboard location:         {dashboard_path.resolve()}")
        print("="*60)
        print("\n✨ Happy job hunting! ✨\n")


def main():
    """
    CLI entry point for InternHunt application.
    
    Usage:
        python -m src.main                    # Without resume
        python -m src.main path/to/resume.pdf # With resume
    """
    # Parse command line arguments
    resume_path = None
    if len(sys.argv) > 1:
        resume_path = Path(sys.argv[1])
        if not resume_path.exists():
            print(f"Error: Resume file not found: {resume_path}")
            sys.exit(1)
    
    # Create and run application
    app = InternHuntApp()
    app.run(resume_path)


if __name__ == "__main__":
    main()
