"""
Internshala Scraper Module

Scrapes internship listings from Internshala.com
"""

from typing import List
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, JobListing
from ..logging_config import get_logger


logger = get_logger(__name__)


class InternshalaScr(BaseScraper):
    """
    Scraper for Internshala platform.
    
    Internshala is one of India's largest internship platforms.
    """
    
    BASE_URL = "https://internshala.com"
    SEARCH_URL = "https://internshala.com/internships"
    
    def scrape(self, preferences) -> List[JobListing]:
        """
        Scrape internship listings from Internshala with pagination support.
        
        Args:
            preferences: UserPreferences object with search criteria
            
        Returns:
            List[JobListing]: List of scraped job listings
        """
        logger.info("Starting Internshala scraping...")
        listings = []
        max_pages = 5  # Scrape first 5 pages for more results
        
        try:
            # Build base search URL with filters
            search_params = self._build_search_params(preferences)
            base_url = f"{self.SEARCH_URL}/{search_params}" if search_params else self.SEARCH_URL
            
            # Scrape multiple pages
            for page in range(1, max_pages + 1):
                logger.info(f"Scraping Internshala page {page}/{max_pages}...")
                
                # Add page parameter
                page_url = f"{base_url}/page-{page}" if page > 1 else base_url
                
                # Make request
                response = self._make_request(page_url)
                if not response:
                    logger.warning(f"Failed to fetch Internshala page {page}")
                    continue
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try multiple selector strategies
                internship_cards = self._find_internship_cards(soup)
                
                if not internship_cards:
                    logger.warning(f"No internship cards found on page {page}")
                    break  # No more results
                
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
                        logger.debug(f"Error parsing Internshala card: {e}")
                        continue
                
                logger.info(f"Extracted {page_listings} listings from page {page}")
                
                # If we got very few results, probably no more pages
                if page_listings < 5:
                    break
            
            logger.info(f"Successfully scraped {len(listings)} total listings from Internshala")
            
        except Exception as e:
            logger.error(f"Error scraping Internshala: {e}")
        
        return listings
    
    def _find_internship_cards(self, soup: BeautifulSoup) -> List:
        """
        Find internship cards using multiple selector strategies.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            List of card elements
        """
        # Try multiple selectors in order of preference
        selectors = [
            ('div', 'internship_meta'),
            ('div', 'individual_internship'),
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
    
    def _build_search_params(self, preferences) -> str:
        """
        Build search parameters for Internshala URL.
        
        Args:
            preferences: UserPreferences object
            
        Returns:
            str: URL parameters string
        """
        params = []
        
        # Add keywords if present - use first keyword only (Internshala limitation)
        if preferences.wanted_keywords:
            # Internshala uses keywords in the URL path
            # Use the first keyword as the main search term
            keyword = preferences.wanted_keywords[0].replace(' ', '-')
            params.append(keyword)
        
        return '/'.join(params)
    
    def _parse_internship_card(self, card) -> JobListing:
        """
        Parse a single internship card from Internshala with multiple fallback selectors.
        
        Args:
            card: BeautifulSoup element representing an internship card
            
        Returns:
            JobListing: Parsed job listing
        """
        # Extract title - try multiple selectors
        title_elem = (card.find('h3', class_='heading_4_5') or 
                     card.find('h4', class_='heading') or
                     card.find('h3') or
                     card.find('h4') or
                     card.find('a', class_='view_detail_button'))
        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
        
        # Extract company - try multiple selectors
        company_elem = (card.find('p', class_='company_name') or 
                       card.find('a', class_='link_display_like_text') or
                       card.find('div', class_='company') or
                       card.find(string=lambda t: t and 'company' in str(t).lower()))
        company = company_elem.get_text(strip=True) if hasattr(company_elem, 'get_text') else str(company_elem).strip() if company_elem else "Unknown Company"
        
        # Extract location - try multiple selectors and fallback to URL parsing
        location_elem = (card.find('p', class_='location_link') or 
                        card.find('span', class_='location') or
                        card.find('div', class_='location') or
                        card.find('a', id=lambda x: x and 'location' in x) or
                        card.find('div', id=lambda x: x and 'location' in str(x).lower()) or
                        card.find(string=lambda t: t and any(city in str(t).lower() for city in ['mumbai', 'delhi', 'bangalore', 'pune', 'hyderabad', 'chennai', 'kolkata'])))
        
        location = "Not specified"
        if location_elem:
            location = location_elem.get_text(strip=True) if hasattr(location_elem, 'get_text') else str(location_elem).strip()
        
        # Fallback: Try to extract location from URL if still not found
        if location == "Not specified":
            # Extract URL first to parse location from it
            link_elem = (card.find('a', class_='view_detail_button') or 
                        card.find('a', class_='view-internship') or
                        card.find('a', href=True))
            if link_elem and link_elem.get('href'):
                url_text = link_elem['href']
                # Look for common city names in URL
                import re
                city_match = re.search(r'in-([\w-]+)-at', url_text)
                if city_match:
                    location = city_match.group(1).replace('-', ' ').title()
                elif 'multiple-locations' in url_text:
                    location = "Multiple locations"
        
        # Extract stipend - try multiple selectors
        stipend_elem = (card.find('span', class_='stipend') or 
                       card.find('div', class_='stipend') or
                       card.find('span', class_='salary') or
                       card.find(string=lambda t: t and '₹' in str(t)))
        raw_stipend_text = stipend_elem.get_text(strip=True) if hasattr(stipend_elem, 'get_text') else str(stipend_elem).strip() if stipend_elem else "Not disclosed"
        stipend = self._parse_stipend(raw_stipend_text)
        
        # Extract description - try multiple selectors
        description_elem = (card.find('div', class_='internship_other_details_container') or 
                           card.find('div', class_='details') or
                           card.find('div', class_='description') or
                           card.find('p'))
        description = description_elem.get_text(strip=True) if description_elem else ""
        
        # Extract URL - try multiple selectors
        link_elem = (card.find('a', class_='view_detail_button') or 
                    card.find('a', class_='view-internship') or
                    card.find('a', href=True))
        if link_elem and link_elem.get('href'):
            url = link_elem['href']
            if not url.startswith('http'):
                url = f"{self.BASE_URL}{url}"
        else:
            url = self.SEARCH_URL
        
        # Extract posted date - try multiple selectors
        date_elem = (card.find('div', class_='status') or 
                    card.find('span', class_='status') or
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
            source_platform="Internshala",
            raw_stipend_text=raw_stipend_text
        )
