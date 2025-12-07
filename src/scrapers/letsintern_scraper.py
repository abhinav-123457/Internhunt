"""
LetsIntern Scraper Module

Scrapes internship listings from LetsIntern.com
"""

from typing import List
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, JobListing
from ..logging_config import get_logger


logger = get_logger(__name__)


class LetsInternScraper(BaseScraper):
    """
    Scraper for LetsIntern platform.
    
    LetsIntern is an Indian platform focused on internships and early career opportunities.
    """
    
    BASE_URL = "https://www.letsintern.com"
    SEARCH_URL = "https://www.letsintern.com/internships"
    
    def scrape(self, preferences) -> List[JobListing]:
        """
        Scrape internship listings from LetsIntern with pagination support.
        
        Args:
            preferences: UserPreferences object with search criteria
            
        Returns:
            List[JobListing]: List of scraped job listings
        """
        logger.info("Starting LetsIntern scraping...")
        listings = []
        max_pages = 3  # Scrape first 3 pages
        
        try:
            for page in range(1, max_pages + 1):
                logger.info(f"Scraping LetsIntern page {page}/{max_pages}...")
                
                # Build page URL
                page_url = f"{self.SEARCH_URL}?page={page}" if page > 1 else self.SEARCH_URL
                
                # Add extra headers to avoid 403
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0',
                }
                
                # Make request with custom headers
                response = self._make_request(page_url, headers=headers)
                if not response:
                    logger.warning(f"Failed to fetch LetsIntern page {page}")
                    continue
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find internship cards with multiple strategies
                internship_cards = self._find_internship_cards(soup)
                
                if not internship_cards:
                    logger.warning(f"No internship cards found on page {page}")
                    break
                
                logger.info(f"Found {len(internship_cards)} cards on page {page}")
                
                # Parse each card
                page_listings = 0
                for card in internship_cards:
                    try:
                        listing = self._parse_internship_card(card)
                        if listing:
                            listings.append(listing)
                            page_listings += 1
                    except Exception as e:
                        logger.debug(f"Error parsing LetsIntern card: {e}")
                        continue
                
                logger.info(f"Extracted {page_listings} listings from page {page}")
                
                # If we got very few results, probably no more pages
                if page_listings < 5:
                    break
            
            logger.info(f"Successfully scraped {len(listings)} total listings from LetsIntern")
            
        except Exception as e:
            logger.error(f"Error scraping LetsIntern: {e}")
        
        return listings
    
    def _find_internship_cards(self, soup: BeautifulSoup) -> List:
        """
        Find internship cards using multiple selector strategies.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of card elements
        """
        # Try multiple selectors
        selectors = [
            ('div', 'internship-card'),
            ('div', 'card'),
            ('article', 'listing'),
            ('article', None),
        ]
        
        for tag, class_name in selectors:
            if class_name:
                cards = soup.find_all(tag, class_=class_name)
            else:
                cards = soup.find_all(tag)
            
            if cards:
                logger.debug(f"Found {len(cards)} cards using selector: {tag} class={class_name}")
                return cards
        
        # Try with lambda for partial class matching
        cards = soup.find_all('div', class_=lambda x: x and 'internship' in x.lower())
        if cards:
            logger.debug(f"Found {len(cards)} cards using partial class matching")
            return cards
        
        return []
    
    def _parse_internship_card(self, card) -> JobListing:
        """
        Parse a single internship card from LetsIntern with multiple fallback selectors.
        
        Args:
            card: BeautifulSoup element representing an internship card
            
        Returns:
            JobListing: Parsed job listing
        """
        # Extract title - try multiple selectors
        title_elem = (card.find('h3', class_='title') or 
                     card.find('h2') or 
                     card.find('div', class_='internship-title') or
                     card.find('h3') or
                     card.find('h4'))
        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
        
        # Extract company - try multiple selectors
        company_elem = (card.find('div', class_='company') or 
                       card.find('span', class_='company-name') or
                       card.find('p', class_='company') or
                       card.find('div', class_='company-name'))
        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
        
        # Extract location - try multiple selectors
        location_elem = (card.find('div', class_='location') or 
                        card.find('span', class_='location') or
                        card.find('p', class_='location'))
        location = location_elem.get_text(strip=True) if location_elem else "Not specified"
        
        # Extract stipend - try multiple selectors
        stipend_elem = (card.find('div', class_='stipend') or 
                       card.find('span', class_='salary') or
                       card.find('div', class_='salary') or
                       card.find('span', class_='stipend') or
                       card.find(string=lambda t: t and '₹' in str(t)))
        raw_stipend_text = stipend_elem.get_text(strip=True) if hasattr(stipend_elem, 'get_text') else str(stipend_elem).strip() if stipend_elem else "Not disclosed"
        stipend = self._parse_stipend(raw_stipend_text)
        
        # Extract description - try multiple selectors
        description_elem = (card.find('div', class_='description') or 
                           card.find('p', class_='details') or
                           card.find('div', class_='details') or
                           card.find('p'))
        description = description_elem.get_text(strip=True) if description_elem else ""
        
        # Extract URL - try multiple selectors
        link_elem = (card.find('a', class_='apply-link') or 
                    card.find('a', class_='view-details') or
                    card.find('a', href=True))
        if link_elem and link_elem.get('href'):
            url = link_elem['href']
            if not url.startswith('http'):
                url = f"{self.BASE_URL}{url}"
        else:
            url = self.SEARCH_URL
        
        # Extract posted date - try multiple selectors
        date_elem = (card.find('div', class_='posted-date') or 
                    card.find('span', class_='date') or
                    card.find('div', class_='date') or
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
            source_platform="LetsIntern",
            raw_stipend_text=raw_stipend_text
        )
