"""
Base Scraper Module

Provides the BaseScraper class with common functionality for all platform scrapers,
including HTTP request handling, rate limiting, timeout/retry logic, and stipend parsing.
"""

import re
import time
import logging
import random
from dataclasses import dataclass
from typing import Optional, List
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup

from ..logging_config import get_logger


logger = get_logger(__name__)


@dataclass
class JobListing:
    """Represents a single internship listing"""
    title: str
    company: str
    stipend: Optional[int]  # In INR, None if unpaid/not specified
    location: str
    description: str
    url: str
    posted_date: Optional[str]
    source_platform: str
    raw_stipend_text: str  # Original text like "₹15,000-20,000/month"


class BaseScraper(ABC):
    """
    Base class for all platform-specific scrapers.
    
    Provides common functionality:
    - HTTP request handling with User-Agent rotation
    - Rate limiting with configurable delays
    - Timeout and retry logic
    - Stipend parsing with regex
    """
    
    # Common User-Agent strings to rotate through
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    def __init__(self, timeout: int = 15, delay: float = 2.0, max_retries: int = 2):
        """
        Initialize the base scraper.
        
        Args:
            timeout: Request timeout in seconds (default: 15)
            delay: Delay between requests in seconds (default: 2.0)
            max_retries: Maximum number of retry attempts (default: 2)
        """
        self.timeout = timeout
        self.delay = delay
        self.max_retries = max_retries
        self.last_request_time = 0.0
        self.session = requests.Session()
        
        logger.debug(f"Initialized {self.__class__.__name__} with timeout={timeout}s, delay={delay}s")
    
    def _get_random_user_agent(self) -> str:
        """
        Get a random User-Agent string from the pool.
        
        Returns:
            str: Random User-Agent string
        """
        return random.choice(self.USER_AGENTS)
    
    def _enforce_rate_limit(self) -> None:
        """
        Enforce rate limiting by ensuring minimum delay between requests.
        
        This method blocks until the required delay has passed since the last request.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.delay:
            sleep_time = self.delay - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Make an HTTP request with error handling, rate limiting, and retry logic.
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Optional[requests.Response]: Response object if successful, None otherwise
        """
        # Enforce rate limiting
        self._enforce_rate_limit()
        
        # Set default headers with random User-Agent
        headers = kwargs.get('headers', {})
        if 'User-Agent' not in headers:
            headers['User-Agent'] = self._get_random_user_agent()
        kwargs['headers'] = headers
        
        # Set timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        # Attempt request with retry logic
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1}/{self.max_retries + 1})")
                
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                
                logger.debug(f"Request successful: {url} (status {response.status_code})")
                return response
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout for {url} (attempt {attempt + 1}/{self.max_retries + 1})")
                if attempt < self.max_retries:
                    # Exponential backoff
                    backoff_time = 2 ** attempt
                    logger.debug(f"Retrying after {backoff_time}s backoff...")
                    time.sleep(backoff_time)
                    continue
                else:
                    logger.error(f"Request failed after {self.max_retries + 1} attempts: {url}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url}: {e}")
                return None
        
        return None
    
    def _parse_stipend(self, stipend_text: str) -> Optional[int]:
        """
        Parse stipend from text to integer value in INR.
        
        Handles various formats:
        - "₹15,000" -> 15000
        - "15000-20000" -> 15000 (minimum value)
        - "₹15,000-₹20,000/month" -> 15000
        - "Unpaid" -> None
        - "Not disclosed" -> None
        
        Args:
            stipend_text: Raw stipend text from listing
            
        Returns:
            Optional[int]: Stipend amount in INR, or None if unpaid/not specified
        """
        if not stipend_text:
            return None
        
        # Normalize text
        text = stipend_text.lower().strip()
        
        # Check for unpaid/not disclosed indicators
        unpaid_indicators = ['unpaid', 'not disclosed', 'not mentioned', 'n/a', 'na']
        if any(indicator in text for indicator in unpaid_indicators):
            logger.debug(f"Stipend marked as unpaid/not disclosed: {stipend_text}")
            return None
        
        # Extract all numbers from the text
        # Remove currency symbols and commas first
        cleaned_text = re.sub(r'[₹$,]', '', text)
        
        # Find all numbers (including decimals)
        numbers = re.findall(r'\d+(?:\.\d+)?', cleaned_text)
        
        if not numbers:
            logger.debug(f"No numbers found in stipend text: {stipend_text}")
            return None
        
        # Convert to integers (multiply by 1000 if it looks like it's in thousands)
        parsed_numbers = []
        for num_str in numbers:
            try:
                num = float(num_str)
                # If number is less than 1000, it might be in thousands (e.g., "15" meaning "15,000")
                # But only if the original text doesn't have explicit thousand separators
                if num < 1000 and ',' not in stipend_text and 'k' in text.lower():
                    num = num * 1000
                parsed_numbers.append(int(num))
            except ValueError:
                continue
        
        if not parsed_numbers:
            logger.debug(f"Could not parse numbers from stipend text: {stipend_text}")
            return None
        
        # Return minimum value (for ranges like "15000-20000")
        min_stipend = min(parsed_numbers)
        logger.debug(f"Parsed stipend: {stipend_text} -> {min_stipend}")
        return min_stipend
    
    @abstractmethod
    def scrape(self, preferences) -> List[JobListing]:
        """
        Scrape listings from the platform.
        
        This method must be implemented by each platform-specific scraper.
        
        Args:
            preferences: UserPreferences object with search criteria
            
        Returns:
            List[JobListing]: List of scraped job listings
        """
        pass
    
    def __del__(self):
        """Clean up session on deletion"""
        if hasattr(self, 'session'):
            self.session.close()
