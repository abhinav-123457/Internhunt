"""
InternWorld Scraper Module

Scrapes internship listings from InternWorld.in
"""

from typing import List
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, JobListing
from ..logging_config import get_logger


logger = get_logger(__name__)


class InternWorldScraper(BaseScraper):
    """
    Scraper for InternWorld platform.
    
    InternWorld is an Indian platform for internship opportunities.
    """
    
    BASE_URL = "https://www.internworld.in"
    SEARCH_URL = "https://www.internworld.in/internships"
    
    def scrape(self, preferences) -> List[JobListing]:
        """
        Scrape internship listings from InternWorld.
        
        Args:
            preferences: UserPreferences object with search criteria
            
        Returns:
            List[JobListing]: List of scraped job listings
        """
        logger.info("Starting InternWorld scraping...")
        listings = []
        
        try:
            # Make request to internships page
            response = self._make_request(self.SEARCH_URL)
            if not response:
                logger.error("Failed to fetch InternWorld internships page")
                return listings
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find internship listings
            internship_cards = soup.find_all('div', class_='listing')
            
            if not internship_cards:
                # Try alternative selectors
                internship_cards = soup.find_all('div', class_='internship') or soup.find_all('article')
            
            logger.info(f"Found {len(internship_cards)} internship cards on InternWorld")
            
            for card in internship_cards:
                try:
                    listing = self._parse_internship_card(card)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error parsing InternWorld card: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(listings)} listings from InternWorld")
            
        except Exception as e:
            logger.error(f"Error scraping InternWorld: {e}")
        
        return listings
    
    def _parse_internship_card(self, card) -> JobListing:
        """
        Parse a single internship card from InternWorld.
        
        Args:
            card: BeautifulSoup element representing an internship card
            
        Returns:
            JobListing: Parsed job listing
        """
        # Extract title
        title_elem = card.find('h3', class_='job-title') or card.find('h2') or card.find('div', class_='title')
        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
        
        # Extract company
        company_elem = card.find('div', class_='company-name') or card.find('span', class_='company')
        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
        
        # Extract location
        location_elem = card.find('div', class_='job-location') or card.find('span', class_='location')
        location = location_elem.get_text(strip=True) if location_elem else "Not specified"
        
        # Extract stipend
        stipend_elem = card.find('div', class_='stipend') or card.find('span', class_='salary')
        raw_stipend_text = stipend_elem.get_text(strip=True) if stipend_elem else "Not disclosed"
        stipend = self._parse_stipend(raw_stipend_text)
        
        # Extract description
        description_elem = card.find('div', class_='job-description') or card.find('p')
        description = description_elem.get_text(strip=True) if description_elem else ""
        
        # Extract URL
        link_elem = card.find('a', class_='view-details') or card.find('a', href=True)
        if link_elem and link_elem.get('href'):
            url = link_elem['href']
            if not url.startswith('http'):
                url = f"{self.BASE_URL}{url}"
        else:
            url = self.SEARCH_URL
        
        # Extract posted date
        date_elem = card.find('div', class_='posted-on') or card.find('span', class_='date')
        posted_date = date_elem.get_text(strip=True) if date_elem else None
        
        return JobListing(
            title=title,
            company=company,
            stipend=stipend,
            location=location,
            description=description,
            url=url,
            posted_date=posted_date,
            source_platform="InternWorld",
            raw_stipend_text=raw_stipend_text
        )
