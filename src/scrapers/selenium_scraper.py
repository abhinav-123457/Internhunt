"""
Selenium-Based Scraper Module

Provides SeleniumScraper class for scraping JavaScript-heavy websites
that require browser automation.
"""

import time
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from ..logging_config import get_logger


logger = get_logger(__name__)


class SeleniumScraper(BaseScraper):
    """
    Base class for scrapers that need browser automation.
    
    Uses Selenium with Chrome in headless mode to scrape JavaScript-heavy websites.
    Automatically manages ChromeDriver installation via webdriver-manager.
    """
    
    def __init__(self, timeout: int = 20, delay: float = 2.0, max_retries: int = 2, headless: bool = True):
        """
        Initialize the Selenium scraper.
        
        Args:
            timeout: Page load timeout in seconds (default: 20)
            delay: Delay between requests in seconds (default: 2.0)
            max_retries: Maximum number of retry attempts (default: 2)
            headless: Run browser in headless mode (default: True)
        """
        super().__init__(timeout, delay, max_retries)
        self.headless = headless
        self.driver = None
        logger.debug(f"Initialized {self.__class__.__name__} with Selenium (headless={headless})")
    
    def _get_driver(self) -> webdriver.Chrome:
        """
        Get or create a Chrome WebDriver instance.
        
        Returns:
            webdriver.Chrome: Chrome WebDriver instance
        """
        if self.driver is None:
            try:
                # Configure Chrome options
                chrome_options = Options()
                
                if self.headless:
                    chrome_options.add_argument('--headless')
                
                # Additional options for stability
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Set user agent
                chrome_options.add_argument(f'user-agent={self._get_random_user_agent()}')
                
                # Install and setup ChromeDriver automatically
                service = Service(ChromeDriverManager().install())
                
                # Create driver
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.set_page_load_timeout(self.timeout)
                
                logger.info("Chrome WebDriver initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize Chrome WebDriver: {e}")
                raise
        
        return self.driver
    
    def _make_selenium_request(self, url: str, wait_for_selector: Optional[str] = None, 
                               wait_time: int = 10) -> Optional[BeautifulSoup]:
        """
        Make a request using Selenium and return parsed HTML.
        
        Args:
            url: URL to request
            wait_for_selector: CSS selector to wait for before returning (optional)
            wait_time: Maximum time to wait for selector (default: 10 seconds)
            
        Returns:
            Optional[BeautifulSoup]: Parsed HTML or None if failed
        """
        # Enforce rate limiting
        self._enforce_rate_limit()
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Making Selenium request to {url} (attempt {attempt + 1}/{self.max_retries + 1})")
                
                # Get driver
                driver = self._get_driver()
                
                # Navigate to URL
                driver.get(url)
                
                # Wait for specific element if provided
                if wait_for_selector:
                    try:
                        WebDriverWait(driver, wait_time).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                        )
                        logger.debug(f"Found element: {wait_for_selector}")
                    except TimeoutException:
                        logger.warning(f"Timeout waiting for selector: {wait_for_selector}")
                        # Continue anyway, might still have some content
                else:
                    # Just wait a bit for JavaScript to load
                    time.sleep(3)
                
                # Get page source and parse
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                logger.debug(f"Successfully loaded page: {url}")
                return soup
                
            except TimeoutException:
                logger.warning(f"Page load timeout for {url} (attempt {attempt + 1}/{self.max_retries + 1})")
                if attempt < self.max_retries:
                    backoff_time = 2 ** attempt
                    logger.debug(f"Retrying after {backoff_time}s backoff...")
                    time.sleep(backoff_time)
                    continue
                else:
                    logger.error(f"Request failed after {self.max_retries + 1} attempts: {url}")
                    return None
                    
            except WebDriverException as e:
                logger.error(f"WebDriver error for {url}: {e}")
                # Try to recover by recreating driver
                self._close_driver()
                if attempt < self.max_retries:
                    time.sleep(2)
                    continue
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {e}")
                return None
        
        return None
    
    def _close_driver(self):
        """Close the WebDriver if it exists."""
        if self.driver:
            try:
                self.driver.quit()
                logger.debug("Chrome WebDriver closed")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def __del__(self):
        """Clean up WebDriver on deletion."""
        self._close_driver()
        super().__del__()
