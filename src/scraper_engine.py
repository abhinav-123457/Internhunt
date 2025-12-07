"""
Scraper Engine Module

Orchestrates parallel scraping across multiple platforms with error isolation.
Aggregates results from all platforms and handles individual platform failures gracefully.
"""

import logging
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from .scrapers.base_scraper import JobListing, BaseScraper
from .scrapers.internshala_scraper import InternshalaScr
from .scrapers.unstop_scraper import UnstopScraper
from .scrapers.linkedin_scraper import LinkedInScraper
from .scrapers.naukri_scraper import NaukriScraper
from .logging_config import get_logger


logger = get_logger(__name__)


@dataclass
class ScrapingResult:
    """Result from scraping operation"""
    platform: str
    listings: List[JobListing]
    success: bool
    error_message: str = None


class ScraperEngine:
    """
    Orchestrates parallel scraping across multiple internship platforms.
    
    Features:
    - Parallel scraping using ThreadPoolExecutor
    - Error isolation (individual platform failures don't affect others)
    - Aggregation of results from all platforms
    """
    
    def __init__(self, max_workers: int = 6):
        """
        Initialize the scraper engine.
        
        Args:
            max_workers: Maximum number of parallel scraping threads (default: 6)
        """
        self.max_workers = max_workers
        
        # Initialize all platform scrapers
        self.scrapers = [
            InternshalaScr(),
            UnstopScraper(),
            LinkedInScraper(),
            NaukriScraper(),
        ]
        
        logger.info(f"Initialized ScraperEngine with {len(self.scrapers)} scrapers")
    
    def scrape_all(self, preferences) -> List[JobListing]:
        """
        Scrape all platforms in parallel and aggregate results.
        
        Individual platform failures are isolated and logged, but don't prevent
        other platforms from being scraped successfully.
        
        Args:
            preferences: UserPreferences object with search criteria
            
        Returns:
            List[JobListing]: Aggregated list of all successfully scraped listings
        """
        logger.info(f"Starting parallel scraping across {len(self.scrapers)} platforms...")
        
        # Print to console which platforms we're scraping
        platform_names = [s.__class__.__name__.replace('Scraper', '').replace('Scr', '') for s in self.scrapers]
        print(f"Scraping from: {', '.join(platform_names)}")
        
        all_listings = []
        scraping_results = []
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scraping tasks
            future_to_scraper = {
                executor.submit(self._scrape_platform, scraper, preferences): scraper
                for scraper in self.scrapers
            }
            
            # Process results as they complete
            for future in as_completed(future_to_scraper):
                scraper = future_to_scraper[future]
                platform_name = scraper.__class__.__name__
                
                try:
                    result = future.result()
                    scraping_results.append(result)
                    
                    if result.success:
                        logger.info(f"✓ {result.platform}: {len(result.listings)} listings")
                        print(f"✓ {result.platform}: {len(result.listings)} listings")
                        all_listings.extend(result.listings)
                    else:
                        logger.warning(f"✗ {result.platform}: {result.error_message}")
                        print(f"✗ {result.platform}: Failed")
                        
                except Exception as e:
                    # This should rarely happen as exceptions are caught in _scrape_platform
                    logger.error(f"✗ {platform_name}: Unexpected error - {e}")
                    scraping_results.append(ScrapingResult(
                        platform=platform_name,
                        listings=[],
                        success=False,
                        error_message=f"Unexpected error: {e}"
                    ))
        
        # Log summary
        successful_platforms = sum(1 for r in scraping_results if r.success)
        failed_platforms = len(scraping_results) - successful_platforms
        
        logger.info(f"Scraping complete: {len(all_listings)} total listings from "
                   f"{successful_platforms}/{len(self.scrapers)} platforms")
        
        if failed_platforms > 0:
            logger.warning(f"{failed_platforms} platform(s) failed to scrape")
        
        return all_listings
    
    def _scrape_platform(self, scraper: BaseScraper, preferences) -> ScrapingResult:
        """
        Scrape a single platform with error isolation.
        
        This method ensures that exceptions from one platform don't affect others.
        
        Args:
            scraper: Platform-specific scraper instance
            preferences: UserPreferences object
            
        Returns:
            ScrapingResult: Result of the scraping operation
        """
        platform_name = scraper.__class__.__name__.replace('Scraper', '').replace('Scr', '')
        
        try:
            logger.debug(f"Starting scraping for {platform_name}...")
            listings = scraper.scrape(preferences)
            
            return ScrapingResult(
                platform=platform_name,
                listings=listings,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error scraping {platform_name}: {e}", exc_info=True)
            return ScrapingResult(
                platform=platform_name,
                listings=[],
                success=False,
                error_message=str(e)
            )
