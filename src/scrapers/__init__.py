"""
Scrapers Package

Contains base scraper infrastructure and platform-specific scrapers
for retrieving internship listings from various job platforms.
"""

from .base_scraper import BaseScraper, JobListing
from .internshala_scraper import InternshalaScr
from .unstop_scraper import UnstopScraper
from .naukri_scraper import NaukriScraper
from .linkedin_scraper import LinkedInScraper
from .letsintern_scraper import LetsInternScraper
from .internworld_scraper import InternWorldScraper

__all__ = [
    'BaseScraper',
    'JobListing',
    'InternshalaScr',
    'UnstopScraper',
    'NaukriScraper',
    'LinkedInScraper',
    'LetsInternScraper',
    'InternWorldScraper',
]
