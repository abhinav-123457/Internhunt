"""
Naukri Scraper Module

Scrapes internship listings from Naukri.com using Selenium.
"""

from typing import List
import time

from .selenium_scraper import SeleniumScraper
from .base_scraper import JobListing
from ..logging_config import get_logger


logger = get_logger(__name__)


class NaukriScraper(SeleniumScraper):
    """
    Scraper for Naukri platform using Selenium.
    
    Naukri.com is one of India's leading job portals.
    """
    
    BASE_URL = "https://www.naukri.com"
    SEARCH_URL = "https://www.naukri.com/internship-jobs"
    
    def scrape(self, preferences) -> List[JobListing]:
        """
        Scrape internship listings from Naukri using Selenium.
        
        Args:
            preferences: UserPreferences object with search criteria
            
        Returns:
            List[JobListing]: List of scraped job listings
        """
        logger.info("Starting Naukri scraping with Selenium...")
        listings = []
        max_pages = 5  # Scrape 5 pages for more results
        
        try:
            # Build base search URL
            search_url = self._build_search_url(preferences)
            
            for page in range(1, max_pages + 1):
                logger.info(f"Scraping Naukri page {page}/{max_pages}...")
                
                # Add page parameter
                page_url = f"{search_url}?page={page}" if page > 1 else search_url
                
                # Load page with Selenium
                soup = self._make_selenium_request(
                    page_url,
                    wait_for_selector='article.jobTuple, div.srp-jobtuple-wrapper',
                    wait_time=10
                )
                
                if not soup:
                    logger.warning(f"Failed to load Naukri page {page}")
                    continue
                
                # Find job cards
                job_cards = soup.find_all('article', class_='jobTuple')
                if not job_cards:
                    job_cards = soup.find_all('div', class_='srp-jobtuple-wrapper')
                
                logger.info(f"Found {len(job_cards)} job cards on page {page}")
                
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
                        logger.debug(f"Error parsing Naukri card: {e}")
                        continue
                
                logger.info(f"Extracted {page_listings} listings from page {page}")
                
                if page_listings < 5:
                    break
            
            logger.info(f"Successfully scraped {len(listings)} total listings from Naukri")
            
        except Exception as e:
            logger.error(f"Error scraping Naukri: {e}")
        finally:
            self._close_driver()
        
        return listings
    
    def _build_search_url(self, preferences) -> str:
        """
        Build search URL with keywords for Naukri.
        
        Args:
            preferences: UserPreferences object
            
        Returns:
            str: Complete search URL
        """
        if preferences.wanted_keywords:
            # Use first keyword only (Naukri URL limitation)
            keyword = preferences.wanted_keywords[0].replace(' ', '-')
            return f"{self.SEARCH_URL}-{keyword}"
        return self.SEARCH_URL
    
    def _parse_job_card(self, card) -> JobListing:
        """
        Parse a single job card from Naukri.
        
        Args:
            card: BeautifulSoup element representing a job card
            
        Returns:
            JobListing: Parsed job listing
        """
        # Extract title
        title_elem = (card.find('a', class_='title') or
                     card.find('h2') or
                     card.find('h3'))
        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
        
        # Extract company
        company_elem = (card.find('a', class_='comp-name') or
                       card.find('div', class_='companyInfo') or
                       card.find('span', class_='company'))
        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
        
        # Extract location
        location_elem = (card.find('span', class_='loc') or
                        card.find('li', class_='location') or
                        card.find('span', class_='location'))
        location = location_elem.get_text(strip=True) if location_elem else "Not specified"
        
        # Extract stipend/salary
        stipend_elem = (card.find('span', class_='sal') or
                       card.find('li', class_='salary') or
                       card.find('span', class_='salary'))
        raw_stipend_text = stipend_elem.get_text(strip=True) if stipend_elem else "Not disclosed"
        stipend = self._parse_stipend(raw_stipend_text)
        
        # Extract description
        description_elem = (card.find('div', class_='job-description') or
                           card.find('ul', class_='details') or
                           card.find('div', class_='description'))
        description = description_elem.get_text(strip=True) if description_elem else ""
        
        # Extract URL
        link_elem = (card.find('a', class_='title') or
                    card.find('a', href=True))
        if link_elem and link_elem.get('href'):
            url = link_elem['href']
            if not url.startswith('http'):
                url = f"{self.BASE_URL}{url}"
        else:
            url = self.SEARCH_URL
        
        # Extract posted date
        date_elem = (card.find('span', class_='date') or
                    card.find('div', class_='jobTupleFooter'))
        posted_date = date_elem.get_text(strip=True) if date_elem else None
        
        return JobListing(
            title=title,
            company=company,
            stipend=stipend,
            location=location,
            description=description,
            url=url,
            posted_date=posted_date,
            source_platform="Naukri",
            raw_stipend_text=raw_stipend_text
        )
