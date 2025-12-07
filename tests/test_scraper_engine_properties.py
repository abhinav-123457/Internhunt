"""
Property-Based Tests for Scraper Engine Module

Tests universal properties that should hold across all inputs.
"""

from hypothesis import given, strategies as st, settings
from src.scraper_engine import ScraperEngine, ScrapingResult
from src.scrapers.base_scraper import BaseScraper, JobListing
from src.preference_wizard import UserPreferences


class MockSuccessfulScraper(BaseScraper):
    """Mock scraper that always succeeds"""
    
    def __init__(self, platform_name="MockSuccess", num_listings=5):
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
    
    def __init__(self, platform_name="MockFail", error_message="Mock error"):
        super().__init__()
        self.platform_name = platform_name
        self.error_message = error_message
    
    def scrape(self, preferences):
        """Raise an exception"""
        raise Exception(self.error_message)


class TestScraperErrorIsolationProperties:
    """
    Property-based tests for scraper error isolation.
    
    **Feature: internhunt-v6, Property 3: Scraper error isolation**
    **Validates: Requirements 3.3, 8.2**
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        num_successful=st.integers(min_value=1, max_value=5),
        num_failing=st.integers(min_value=1, max_value=5),
        listings_per_scraper=st.integers(min_value=1, max_value=10)
    )
    def test_error_isolation_continues_on_failure(self, num_successful, num_failing, listings_per_scraper):
        """
        Property: For any scraping operation where one or more platforms fail,
        the system should continue processing remaining platforms and return
        all successfully scraped listings.
        
        This test verifies that:
        1. Failed scrapers don't prevent successful scrapers from running
        2. All listings from successful scrapers are returned
        3. The total count matches expected successful listings
        """
        # Create mock preferences
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
        
        # Create engine with mixed successful and failing scrapers
        engine = ScraperEngine(max_workers=num_successful + num_failing)
        
        # Replace scrapers with mock scrapers
        engine.scrapers = []
        
        # Add successful scrapers
        for i in range(num_successful):
            engine.scrapers.append(
                MockSuccessfulScraper(
                    platform_name=f"Success{i}",
                    num_listings=listings_per_scraper
                )
            )
        
        # Add failing scrapers
        for i in range(num_failing):
            engine.scrapers.append(
                MockFailingScraper(
                    platform_name=f"Fail{i}",
                    error_message=f"Error from platform {i}"
                )
            )
        
        # Scrape all platforms
        results = engine.scrape_all(preferences)
        
        # Verify that we got listings from all successful scrapers
        expected_total = num_successful * listings_per_scraper
        assert len(results) == expected_total, \
            f"Expected {expected_total} listings from {num_successful} successful scrapers, got {len(results)}"
        
        # Verify all results are JobListing objects
        assert all(isinstance(listing, JobListing) for listing in results), \
            "All results should be JobListing objects"
        
        # Verify that listings came from successful scrapers only
        successful_platforms = {f"Success{i}" for i in range(num_successful)}
        result_platforms = {listing.source_platform for listing in results}
        
        assert result_platforms.issubset(successful_platforms), \
            f"Results contain listings from unexpected platforms: {result_platforms - successful_platforms}"
    
    @settings(max_examples=100, deadline=None)
    @given(
        num_scrapers=st.integers(min_value=2, max_value=6),
        failure_indices=st.lists(st.integers(min_value=0, max_value=5), min_size=1, max_size=3, unique=True)
    )
    def test_partial_failure_returns_successful_results(self, num_scrapers, failure_indices):
        """
        Property: When some (but not all) scrapers fail, the system should
        return results from the successful scrapers.
        
        This test verifies that partial failures don't result in empty results.
        """
        # Filter failure indices to be within range
        failure_indices = [idx for idx in failure_indices if idx < num_scrapers]
        
        # Skip if all scrapers would fail
        if len(failure_indices) >= num_scrapers:
            return
        
        # Create mock preferences
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
        
        # Create engine
        engine = ScraperEngine(max_workers=num_scrapers)
        engine.scrapers = []
        
        # Add scrapers (some successful, some failing)
        for i in range(num_scrapers):
            if i in failure_indices:
                engine.scrapers.append(MockFailingScraper(platform_name=f"Platform{i}"))
            else:
                engine.scrapers.append(MockSuccessfulScraper(platform_name=f"Platform{i}", num_listings=3))
        
        # Scrape all platforms
        results = engine.scrape_all(preferences)
        
        # Calculate expected successful scrapers
        num_successful = num_scrapers - len(failure_indices)
        expected_listings = num_successful * 3
        
        # Verify we got results from successful scrapers
        assert len(results) == expected_listings, \
            f"Expected {expected_listings} listings from {num_successful} successful scrapers, got {len(results)}"
        
        # Verify no results from failed scrapers
        failed_platforms = {f"Platform{i}" for i in failure_indices}
        result_platforms = {listing.source_platform for listing in results}
        
        assert not result_platforms.intersection(failed_platforms), \
            f"Results should not contain listings from failed platforms: {result_platforms.intersection(failed_platforms)}"
    
    @settings(max_examples=100, deadline=None)
    @given(
        num_scrapers=st.integers(min_value=1, max_value=6)
    )
    def test_all_failures_returns_empty_list(self, num_scrapers):
        """
        Property: When all scrapers fail, the system should return an empty list
        (not crash or raise an exception).
        
        This test verifies graceful handling of complete failure scenarios.
        """
        # Create mock preferences
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
        
        # Create engine with all failing scrapers
        engine = ScraperEngine(max_workers=num_scrapers)
        engine.scrapers = [
            MockFailingScraper(platform_name=f"Fail{i}", error_message=f"Error {i}")
            for i in range(num_scrapers)
        ]
        
        # Scrape all platforms - should not raise exception
        results = engine.scrape_all(preferences)
        
        # Verify empty results
        assert results == [], \
            f"Expected empty list when all scrapers fail, got {len(results)} listings"
        
        # Verify result is a list (not None or other type)
        assert isinstance(results, list), \
            f"Expected list type, got {type(results)}"
    
    @settings(max_examples=100, deadline=None)
    @given(
        num_successful=st.integers(min_value=1, max_value=5),
        listings_per_scraper=st.lists(
            st.integers(min_value=0, max_value=10),
            min_size=1,
            max_size=5
        )
    )
    def test_aggregation_preserves_all_listings(self, num_successful, listings_per_scraper):
        """
        Property: The aggregated results should contain exactly the sum of
        all listings from successful scrapers (no duplicates added, no listings lost).
        
        This test verifies that aggregation doesn't lose or duplicate data.
        """
        # Adjust listings_per_scraper to match num_successful
        if len(listings_per_scraper) > num_successful:
            listings_per_scraper = listings_per_scraper[:num_successful]
        elif len(listings_per_scraper) < num_successful:
            listings_per_scraper = listings_per_scraper + [5] * (num_successful - len(listings_per_scraper))
        
        # Create mock preferences
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
        
        # Create engine with successful scrapers
        engine = ScraperEngine(max_workers=num_successful)
        engine.scrapers = [
            MockSuccessfulScraper(
                platform_name=f"Platform{i}",
                num_listings=listings_per_scraper[i]
            )
            for i in range(num_successful)
        ]
        
        # Scrape all platforms
        results = engine.scrape_all(preferences)
        
        # Calculate expected total
        expected_total = sum(listings_per_scraper)
        
        # Verify total count
        assert len(results) == expected_total, \
            f"Expected {expected_total} total listings, got {len(results)}"
        
        # Verify each platform contributed the correct number of listings
        for i in range(num_successful):
            platform_name = f"Platform{i}"
            platform_listings = [l for l in results if l.source_platform == platform_name]
            expected_count = listings_per_scraper[i]
            
            assert len(platform_listings) == expected_count, \
                f"Expected {expected_count} listings from {platform_name}, got {len(platform_listings)}"
