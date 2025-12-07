"""
Unit Tests for Scraper Engine Module

Tests basic functionality and integration of the scraper engine.
"""

import pytest
from src.scraper_engine import ScraperEngine, ScrapingResult
from src.scrapers.base_scraper import BaseScraper, JobListing
from src.preference_wizard import UserPreferences


class MockSuccessfulScraper(BaseScraper):
    """Mock scraper that always succeeds"""
    
    def __init__(self, platform_name="MockSuccess", num_listings=3):
        super().__init__()
        self.platform_name = platform_name
        self.num_listings = num_listings
    
    def scrape(self, preferences):
        """Return mock listings"""
        return [
            JobListing(
                title=f"Job {i}",
                company=f"Company {i}",
                stipend=10000 + i * 1000,
                location="Remote",
                description=f"Description {i}",
                url=f"https://example.com/job{i}",
                posted_date="1 day ago",
                source_platform=self.platform_name,
                raw_stipend_text=f"₹{10000 + i * 1000}"
            )
            for i in range(self.num_listings)
        ]


class MockFailingScraper(BaseScraper):
    """Mock scraper that always fails"""
    
    def __init__(self, platform_name="MockFail"):
        super().__init__()
        self.platform_name = platform_name
    
    def scrape(self, preferences):
        """Raise an exception"""
        raise Exception("Mock scraping error")


class TestScraperEngineInitialization:
    """Tests for ScraperEngine initialization"""
    
    def test_engine_initializes_with_all_scrapers(self):
        """Test that engine initializes with all 4 platform scrapers"""
        engine = ScraperEngine()
        
        assert len(engine.scrapers) == 4, "Engine should initialize with 4 scrapers (Internshala, Unstop, LinkedIn, Naukri)"
        assert engine.max_workers == 6, "Default max_workers should be 6"
    
    def test_engine_accepts_custom_max_workers(self):
        """Test that engine accepts custom max_workers parameter"""
        engine = ScraperEngine(max_workers=3)
        
        assert engine.max_workers == 3, "Engine should use custom max_workers"


class TestScraperEngineErrorIsolation:
    """Tests for error isolation functionality"""
    
    def test_single_scraper_failure_does_not_affect_others(self):
        """Test that one failing scraper doesn't prevent others from succeeding"""
        preferences = UserPreferences(
            wanted_keywords=["python"],
            reject_keywords=[],
            remote_preference="any",
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        engine = ScraperEngine()
        engine.scrapers = [
            MockSuccessfulScraper("Platform1", 5),
            MockFailingScraper("Platform2"),
            MockSuccessfulScraper("Platform3", 3),
        ]
        
        results = engine.scrape_all(preferences)
        
        # Should get 8 listings (5 + 3) from successful scrapers
        assert len(results) == 8, f"Expected 8 listings, got {len(results)}"
        
        # Verify listings are from successful platforms only
        platforms = {listing.source_platform for listing in results}
        assert platforms == {"Platform1", "Platform3"}, \
            f"Expected listings from Platform1 and Platform3, got {platforms}"
    
    def test_all_scrapers_fail_returns_empty_list(self):
        """Test that all failures result in empty list, not exception"""
        preferences = UserPreferences(
            wanted_keywords=["python"],
            reject_keywords=[],
            remote_preference="any",
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        engine = ScraperEngine()
        engine.scrapers = [
            MockFailingScraper("Platform1"),
            MockFailingScraper("Platform2"),
            MockFailingScraper("Platform3"),
        ]
        
        # Should not raise exception
        results = engine.scrape_all(preferences)
        
        assert results == [], "Expected empty list when all scrapers fail"
    
    def test_all_scrapers_succeed_returns_all_listings(self):
        """Test that all successful scrapers contribute their listings"""
        preferences = UserPreferences(
            wanted_keywords=["python"],
            reject_keywords=[],
            remote_preference="any",
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        engine = ScraperEngine()
        engine.scrapers = [
            MockSuccessfulScraper("Platform1", 2),
            MockSuccessfulScraper("Platform2", 3),
            MockSuccessfulScraper("Platform3", 4),
        ]
        
        results = engine.scrape_all(preferences)
        
        # Should get 9 listings total (2 + 3 + 4)
        assert len(results) == 9, f"Expected 9 listings, got {len(results)}"
        
        # Verify each platform contributed correct number
        platform1_listings = [l for l in results if l.source_platform == "Platform1"]
        platform2_listings = [l for l in results if l.source_platform == "Platform2"]
        platform3_listings = [l for l in results if l.source_platform == "Platform3"]
        
        assert len(platform1_listings) == 2, "Platform1 should contribute 2 listings"
        assert len(platform2_listings) == 3, "Platform2 should contribute 3 listings"
        assert len(platform3_listings) == 4, "Platform3 should contribute 4 listings"


class TestScraperEngineAggregation:
    """Tests for result aggregation"""
    
    def test_aggregation_preserves_listing_data(self):
        """Test that aggregation preserves all listing data correctly"""
        preferences = UserPreferences(
            wanted_keywords=["python"],
            reject_keywords=[],
            remote_preference="any",
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        engine = ScraperEngine()
        engine.scrapers = [
            MockSuccessfulScraper("TestPlatform", 2),
        ]
        
        results = engine.scrape_all(preferences)
        
        # Verify all listings have required fields
        for listing in results:
            assert isinstance(listing, JobListing), "Result should be JobListing"
            assert listing.title, "Listing should have title"
            assert listing.company, "Listing should have company"
            assert listing.url, "Listing should have URL"
            assert listing.source_platform == "TestPlatform", "Listing should have correct platform"
    
    def test_empty_scraper_results_handled_correctly(self):
        """Test that scrapers returning empty lists are handled correctly"""
        preferences = UserPreferences(
            wanted_keywords=["python"],
            reject_keywords=[],
            remote_preference="any",
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        engine = ScraperEngine()
        engine.scrapers = [
            MockSuccessfulScraper("Platform1", 0),  # Returns empty list
            MockSuccessfulScraper("Platform2", 3),
            MockSuccessfulScraper("Platform3", 0),  # Returns empty list
        ]
        
        results = engine.scrape_all(preferences)
        
        # Should only get 3 listings from Platform2
        assert len(results) == 3, f"Expected 3 listings, got {len(results)}"
        assert all(l.source_platform == "Platform2" for l in results), \
            "All listings should be from Platform2"
