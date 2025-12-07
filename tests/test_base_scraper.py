"""
Unit Tests for Base Scraper Module

Tests stipend parsing functionality and other base scraper features.
"""

import pytest
from src.scrapers.base_scraper import BaseScraper, JobListing


class MockScraper(BaseScraper):
    """Mock scraper for testing base functionality"""
    
    def scrape(self, preferences):
        """Mock implementation"""
        return []


class TestStipendParsing:
    """Test suite for stipend parsing functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.scraper = MockScraper()
    
    def test_parse_simple_rupee_format(self):
        """Test parsing simple rupee format with comma separator"""
        assert self.scraper._parse_stipend("₹15,000") == 15000
        assert self.scraper._parse_stipend("₹20,000") == 20000
        assert self.scraper._parse_stipend("₹5,000") == 5000
    
    def test_parse_range_format(self):
        """Test parsing range format - should return minimum value"""
        assert self.scraper._parse_stipend("15000-20000") == 15000
        assert self.scraper._parse_stipend("₹10,000-₹15,000") == 10000
        assert self.scraper._parse_stipend("₹5,000 - ₹10,000") == 5000
        assert self.scraper._parse_stipend("8000-12000") == 8000
    
    def test_parse_range_with_month_suffix(self):
        """Test parsing range with /month suffix"""
        assert self.scraper._parse_stipend("₹15,000-₹20,000/month") == 15000
        assert self.scraper._parse_stipend("10000-15000/month") == 10000
        assert self.scraper._parse_stipend("₹8,000 - ₹12,000 per month") == 8000
    
    def test_parse_unpaid(self):
        """Test parsing unpaid stipend indicators"""
        assert self.scraper._parse_stipend("Unpaid") is None
        assert self.scraper._parse_stipend("unpaid") is None
        assert self.scraper._parse_stipend("UNPAID") is None
        assert self.scraper._parse_stipend("Unpaid Internship") is None
    
    def test_parse_not_disclosed(self):
        """Test parsing not disclosed indicators"""
        assert self.scraper._parse_stipend("Not disclosed") is None
        assert self.scraper._parse_stipend("Not Disclosed") is None
        assert self.scraper._parse_stipend("Not mentioned") is None
        assert self.scraper._parse_stipend("N/A") is None
        assert self.scraper._parse_stipend("NA") is None
    
    def test_parse_empty_or_none(self):
        """Test parsing empty or None stipend"""
        assert self.scraper._parse_stipend("") is None
        assert self.scraper._parse_stipend(None) is None
        assert self.scraper._parse_stipend("   ") is None
    
    def test_parse_without_currency_symbol(self):
        """Test parsing numbers without currency symbols"""
        assert self.scraper._parse_stipend("15000") == 15000
        assert self.scraper._parse_stipend("20000") == 20000
        assert self.scraper._parse_stipend("10,000") == 10000
    
    def test_parse_with_dollar_sign(self):
        """Test parsing with dollar sign (some platforms might use it)"""
        assert self.scraper._parse_stipend("$500") == 500
        assert self.scraper._parse_stipend("$1,000") == 1000
    
    def test_parse_with_k_suffix(self):
        """Test parsing with 'k' suffix for thousands"""
        assert self.scraper._parse_stipend("15k") == 15000
        assert self.scraper._parse_stipend("20K") == 20000
        assert self.scraper._parse_stipend("₹10k") == 10000
    
    def test_parse_complex_format(self):
        """Test parsing complex formats with extra text"""
        assert self.scraper._parse_stipend("Stipend: ₹15,000 per month") == 15000
        assert self.scraper._parse_stipend("₹10,000 - ₹15,000 (Performance based)") == 10000
        assert self.scraper._parse_stipend("Between ₹8,000 and ₹12,000") == 8000
    
    def test_parse_decimal_values(self):
        """Test parsing decimal values (should convert to int)"""
        assert self.scraper._parse_stipend("15000.50") == 15000
        assert self.scraper._parse_stipend("₹10,500.75") == 10500
    
    def test_parse_invalid_text(self):
        """Test parsing text with no valid numbers"""
        assert self.scraper._parse_stipend("To be decided") is None
        assert self.scraper._parse_stipend("Negotiable") is None
        assert self.scraper._parse_stipend("Based on performance") is None


class TestRateLimiting:
    """Test suite for rate limiting functionality"""
    
    def test_rate_limit_enforced(self):
        """Test that rate limiting enforces minimum delay"""
        import time
        
        scraper = MockScraper(delay=0.5)
        
        # Make first request
        start_time = time.time()
        scraper._enforce_rate_limit()
        
        # Make second request immediately
        scraper._enforce_rate_limit()
        elapsed = time.time() - start_time
        
        # Should have waited at least the delay time
        assert elapsed >= 0.5
    
    def test_rate_limit_no_wait_after_delay(self):
        """Test that no wait occurs if enough time has passed"""
        import time
        
        scraper = MockScraper(delay=0.1)
        
        # Make first request
        scraper._enforce_rate_limit()
        
        # Wait longer than delay
        time.sleep(0.2)
        
        # Second request should not wait
        start_time = time.time()
        scraper._enforce_rate_limit()
        elapsed = time.time() - start_time
        
        # Should be nearly instant (less than 0.05s)
        assert elapsed < 0.05


class TestUserAgentRotation:
    """Test suite for User-Agent rotation"""
    
    def test_user_agent_selection(self):
        """Test that User-Agent is selected from pool"""
        scraper = MockScraper()
        user_agent = scraper._get_random_user_agent()
        
        assert user_agent in BaseScraper.USER_AGENTS
        assert len(user_agent) > 0
    
    def test_user_agent_variety(self):
        """Test that User-Agent rotation provides variety"""
        scraper = MockScraper()
        
        # Get multiple user agents
        agents = [scraper._get_random_user_agent() for _ in range(20)]
        
        # Should have at least 2 different agents in 20 selections
        # (statistically very likely with 5 options)
        unique_agents = set(agents)
        assert len(unique_agents) >= 2


class TestJobListingDataclass:
    """Test suite for JobListing dataclass"""
    
    def test_job_listing_creation(self):
        """Test creating a JobListing instance"""
        listing = JobListing(
            title="ML Intern",
            company="TechCorp",
            stipend=15000,
            location="Bangalore",
            description="Machine learning internship",
            url="https://example.com/job/123",
            posted_date="2024-01-01",
            source_platform="TestPlatform",
            raw_stipend_text="₹15,000/month"
        )
        
        assert listing.title == "ML Intern"
        assert listing.company == "TechCorp"
        assert listing.stipend == 15000
        assert listing.location == "Bangalore"
        assert listing.description == "Machine learning internship"
        assert listing.url == "https://example.com/job/123"
        assert listing.posted_date == "2024-01-01"
        assert listing.source_platform == "TestPlatform"
        assert listing.raw_stipend_text == "₹15,000/month"
    
    def test_job_listing_with_none_values(self):
        """Test creating a JobListing with None values"""
        listing = JobListing(
            title="Unpaid Intern",
            company="StartupCo",
            stipend=None,
            location="Remote",
            description="Unpaid internship",
            url="https://example.com/job/456",
            posted_date=None,
            source_platform="TestPlatform",
            raw_stipend_text="Unpaid"
        )
        
        assert listing.stipend is None
        assert listing.posted_date is None
