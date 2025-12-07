"""
LinkedIn Scraper Module

Scrapes internship listings from LinkedIn.com using Selenium for JavaScript rendering.
"""

from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from .selenium_scraper import SeleniumScraper
from .base_scraper import JobListing
from ..logging_config import get_logger


logger = get_logger(__name__)


class LinkedInScraper(SeleniumScraper):
    """
    Scraper for LinkedIn platform using Selenium.
    
    LinkedIn uses heavy JavaScript, so we need browser automation.
    """
    
    BASE_URL = "https://www.linkedin.com"
    SEARCH_URL = "https://www.linkedin.com/jobs/search"
    
    def scrape(self, preferences) -> List[JobListing]:
        """
        Scrape internship listings from LinkedIn using Selenium.
        
        Args:
            preferences: UserPreferences object with search criteria
            
        Returns:
            List[JobListing]: List of scraped job listings
        """
        logger.info("Starting LinkedIn scraping with Selenium...")
        listings = []
        max_pages = 5  # Scrape 5 pages to get more results (125 listings max)
        
        try:
            # Build search URL
            search_params = self._build_search_params(preferences)
            base_url = f"{self.SEARCH_URL}?{search_params}"
            
            for page in range(max_pages):
                logger.info(f"Scraping LinkedIn page {page + 1}/{max_pages}...")
                
                # Add page offset
                page_url = f"{base_url}&start={page * 25}"
                
                # Load page with Selenium - try multiple selectors
                soup = None
                selectors_to_try = [
                    'ul.jobs-search__results-list',
                    'div.jobs-search-results-list',
                    'div.scaffold-layout__list',
                    'ul.scaffold-layout__list-container'
                ]
                
                for selector in selectors_to_try:
                    try:
                        soup = self._make_selenium_request(
                            page_url,
                            wait_for_selector=selector,
                            wait_time=10
                        )
                        if soup:
                            logger.info(f"Successfully loaded page with selector: {selector}")
                            break
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {e}")
                        continue
                
                if not soup:
                    logger.warning(f"Failed to load LinkedIn page {page + 1}")
                    continue
                
                # Find job cards - try multiple selectors
                job_cards = soup.find_all('div', class_='base-card')
                if not job_cards:
                    job_cards = soup.find_all('li', class_='jobs-search-results__list-item')
                if not job_cards:
                    job_cards = soup.find_all('div', class_='job-search-card')
                if not job_cards:
                    job_cards = soup.find_all('li', class_='scaffold-layout__list-item')
                
                logger.info(f"Found {len(job_cards)} job cards on page {page + 1}")
                
                if not job_cards:
                    break
                
                # Parse each card
                page_listings = 0
                for card in job_cards:
                    try:
                        listing = self._parse_job_card(card)
                        if listing:
                            listings.append(listing)
                            page_listings += 1
                    except Exception as e:
                        logger.debug(f"Error parsing LinkedIn card: {e}")
                        continue
                
                logger.info(f"Extracted {page_listings} listings from page {page + 1}")
                
                if page_listings < 5:
                    break
            
            logger.info(f"Successfully scraped {len(listings)} total listings from LinkedIn")
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
        finally:
            # Clean up driver
            self._close_driver()
        
        return listings
    
    def _build_search_params(self, preferences) -> str:
        """
        Build search parameters for LinkedIn URL.
        
        Args:
            preferences: UserPreferences object
            
        Returns:
            str: URL parameters string
        """
        params = []
        
        # Add keywords - use ALL keywords for better search results
        if preferences.wanted_keywords:
            # Join all keywords with OR logic for broader search
            keywords = ' OR '.join(preferences.wanted_keywords)
            params.append(f"keywords={keywords.replace(' ', '%20')}")
        
        # Add location (India)
        params.append("location=India")
        
        # Filter for internships and entry level
        params.append("f_JT=I")  # I = Internship
        params.append("f_E=1,2")  # Entry level
        
        # Sort by date
        params.append("sortBy=DD")  # Date descending
        
        return '&'.join(params)
    
    def _parse_job_card(self, card) -> JobListing:
        """
        Parse a single job card from LinkedIn.
        
        Args:
            card: BeautifulSoup element representing a job card
            
        Returns:
            JobListing: Parsed job listing
        """
        # Extract title
        title_elem = (card.find('h3', class_='base-search-card__title') or
                     card.find('a', class_='job-card-list__title') or
                     card.find('h3'))
        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
        
        # Extract company
        company_elem = (card.find('h4', class_='base-search-card__subtitle') or
                       card.find('a', class_='job-card-container__company-name') or
                       card.find('h4'))
        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
        
        # Extract location
        location_elem = (card.find('span', class_='job-search-card__location') or
                        card.find('li', class_='job-card-container__metadata-item'))
        location = location_elem.get_text(strip=True) if location_elem else "Not specified"
        
        # LinkedIn rarely shows stipend in search results
        stipend = None
        raw_stipend_text = "Not disclosed"
        
        # Extract description snippet
        description_elem = card.find('p', class_='job-search-card__snippet')
        description = description_elem.get_text(strip=True) if description_elem else ""
        
        # Extract URL
        link_elem = card.find('a', href=True)
        if link_elem and link_elem.get('href'):
            url = link_elem['href']
            if not url.startswith('http'):
                url = f"{self.BASE_URL}{url}"
        else:
            url = self.SEARCH_URL
        
        # Extract posted date
        date_elem = card.find('time')
        posted_date = date_elem.get('datetime') if date_elem else None
        
        return JobListing(
            title=title,
            company=company,
            stipend=stipend,
            location=location,
            description=description,
            url=url,
            posted_date=posted_date,
            source_platform="LinkedIn",
            raw_stipend_text=raw_stipend_text
        )
