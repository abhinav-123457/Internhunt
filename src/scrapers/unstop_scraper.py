"""
Unstop Scraper Module

Scrapes internship listings from Unstop.com (formerly Dare2Compete) using Selenium.
"""

from typing import List
import time

from .selenium_scraper import SeleniumScraper
from .base_scraper import JobListing
from ..logging_config import get_logger


logger = get_logger(__name__)


class UnstopScraper(SeleniumScraper):
    """
    Scraper for Unstop platform using Selenium.
    
    Unstop uses JavaScript for dynamic content loading.
    """
    
    BASE_URL = "https://unstop.com"
    SEARCH_URL = "https://unstop.com/internships"
    
    def scrape(self, preferences) -> List[JobListing]:
        """
        Scrape internship listings from Unstop using Selenium.
        
        Args:
            preferences: UserPreferences object with search criteria
            
        Returns:
            List[JobListing]: List of scraped job listings
        """
        logger.info("Starting Unstop scraping with Selenium...")
        listings = []
        max_pages = 2
        
        try:
            for page in range(1, max_pages + 1):
                logger.info(f"Scraping Unstop page {page}/{max_pages}...")
                
                # Build page URL
                page_url = f"{self.SEARCH_URL}?page={page}" if page > 1 else self.SEARCH_URL
                
                # Load page with Selenium
                # Load page with Selenium - try multiple selectors
                soup = None
                selectors_to_try = [
                    'div.opportunity-card',
                    'div.card',
                    'div.opportunity',
                    'article',
                    'div[class*="opportunity"]'
                ]
                
                for selector in selectors_to_try:
                    try:
                        soup = self._make_selenium_request(
                            page_url,
                            wait_for_selector=selector,
                            wait_time=8
                        )
                        if soup:
                            logger.info(f"Successfully loaded page with selector: {selector}")
                            break
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {e}")
                        continue
                
                if not soup:
                    logger.warning(f"Failed to load Unstop page {page} with any selector")
                    continue
                
                # Find opportunity cards
                opportunity_cards = soup.find_all('div', class_='opportunity-card')
                if not opportunity_cards:
                    opportunity_cards = soup.find_all('div', class_='card')
                
                logger.info(f"Found {len(opportunity_cards)} cards on page {page}")
                
                if not opportunity_cards:
                    break
                
                # Parse each card
                page_listings = 0
                for card in opportunity_cards:
                    try:
                        listing = self._parse_opportunity_card(card)
                        if listing:
                            listings.append(listing)
                            page_listings += 1
                    except Exception as e:
                        logger.debug(f"Error parsing Unstop card: {e}")
                        continue
                
                logger.info(f"Extracted {page_listings} listings from page {page}")
                
                if page_listings < 5:
                    break
            
            logger.info(f"Successfully scraped {len(listings)} total listings from Unstop")
            
        except Exception as e:
            logger.error(f"Error scraping Unstop: {e}")
        finally:
            self._close_driver()
        
        return listings
    
    def _parse_opportunity_card(self, card) -> JobListing:
        """
        Parse a single opportunity card from Unstop.
        
        Args:
            card: BeautifulSoup element representing an opportunity card
            
        Returns:
            JobListing: Parsed job listing
        """
        # Extract title
        title_elem = (card.find('h3') or
                     card.find('h2') or
                     card.find('div', class_='title') or
                     card.find('a', class_='title'))
        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
        
        # Extract company
        company_elem = (card.find('div', class_='company') or
                       card.find('span', class_='organization') or
                       card.find('div', class_='organization'))
        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
        
        # Extract location
        location_elem = (card.find('div', class_='location') or
                        card.find('span', class_='location'))
        location = location_elem.get_text(strip=True) if location_elem else "Not specified"
        
        # Extract stipend
        stipend_elem = (card.find('div', class_='stipend') or
                       card.find('span', class_='compensation'))
        raw_stipend_text = stipend_elem.get_text(strip=True) if stipend_elem else "Not disclosed"
        stipend = self._parse_stipend(raw_stipend_text)
        
        # Extract description
        description_elem = (card.find('div', class_='description') or
                           card.find('p'))
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
        date_elem = (card.find('div', class_='date') or
                    card.find('span', class_='posted'))
        posted_date = date_elem.get_text(strip=True) if date_elem else None
        
        return JobListing(
            title=title,
            company=company,
            stipend=stipend,
            location=location,
            description=description,
            url=url,
            posted_date=posted_date,
            source_platform="Unstop",
            raw_stipend_text=raw_stipend_text
        )
