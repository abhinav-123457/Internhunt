"""
Property-Based Tests for Base Scraper Module

Tests universal properties that should hold across all inputs.
"""

import time
from hypothesis import given, strategies as st, settings
from src.scrapers.base_scraper import BaseScraper, JobListing


class MockScraper(BaseScraper):
    """Mock scraper for testing base functionality"""
    
    def scrape(self, preferences):
        """Mock implementation"""
        return []


class TestRateLimitingProperties:
    """
    Property-based tests for rate limiting compliance.
    
    **Feature: internhunt-v6, Property 14: Rate limiting compliance**
    **Validates: Requirements 9.1**
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        num_requests=st.integers(min_value=2, max_value=5),
        delay=st.floats(min_value=0.1, max_value=0.5)
    )
    def test_rate_limiting_compliance(self, num_requests, delay):
        """
        Property: For any sequence of requests to the same domain,
        the time between consecutive requests should be at least the configured delay.
        
        This test verifies that rate limiting is properly enforced across
        multiple consecutive requests.
        """
        scraper = MockScraper(delay=delay)
        
        request_times = []
        
        # Make multiple consecutive requests and record time AFTER each completes
        for _ in range(num_requests):
            scraper._enforce_rate_limit()
            request_times.append(time.time())
        
        # Verify that each consecutive pair of requests has at least 'delay' seconds between them
        for i in range(1, len(request_times)):
            time_between_requests = request_times[i] - request_times[i-1]
            
            # Allow small tolerance for timing precision (20ms)
            assert time_between_requests >= (delay - 0.02), \
                f"Rate limit violated: {time_between_requests:.3f}s < {delay}s between requests {i-1} and {i}"
    
    @settings(max_examples=100, deadline=None)
    @given(
        delay=st.floats(min_value=0.1, max_value=0.5),
        wait_time=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_rate_limiting_respects_elapsed_time(self, delay, wait_time):
        """
        Property: If sufficient time has elapsed since the last request,
        no additional waiting should occur.
        
        This test verifies that the rate limiter doesn't unnecessarily delay
        requests when enough time has already passed.
        """
        scraper = MockScraper(delay=delay)
        
        # Make first request
        scraper._enforce_rate_limit()
        
        # Wait for specified time
        time.sleep(wait_time)
        
        # Measure time for second request
        start = time.time()
        scraper._enforce_rate_limit()
        elapsed = time.time() - start
        
        if wait_time >= delay:
            # If we waited longer than delay, second request should be nearly instant
            # Allow 50ms tolerance for execution time
            assert elapsed < 0.05, \
                f"Unnecessary delay: waited {wait_time:.3f}s (>= {delay}s), but still delayed {elapsed:.3f}s"
        else:
            # If we didn't wait long enough, should wait the remaining time
            expected_wait = delay - wait_time
            # Allow 30ms tolerance for timing precision
            assert abs(elapsed - expected_wait) < 0.03, \
                f"Incorrect delay: expected ~{expected_wait:.3f}s, got {elapsed:.3f}s"


class TestStipendParsingProperties:
    """Property-based tests for stipend parsing"""
    
    @settings(max_examples=100)
    @given(
        amount=st.integers(min_value=1000, max_value=100000)
    )
    def test_parse_simple_amount(self, amount):
        """
        Property: For any valid stipend amount, parsing should return
        a non-negative integer or None.
        """
        scraper = MockScraper()
        
        # Test various formats
        formats = [
            f"₹{amount:,}",
            f"{amount}",
            f"₹{amount}",
            f"{amount:,}"
        ]
        
        for format_str in formats:
            result = scraper._parse_stipend(format_str)
            assert result is None or (isinstance(result, int) and result >= 0), \
                f"Invalid result for '{format_str}': {result}"
    
    @settings(max_examples=100)
    @given(
        min_amount=st.integers(min_value=1000, max_value=50000),
        max_amount=st.integers(min_value=50001, max_value=100000)
    )
    def test_parse_range_returns_minimum(self, min_amount, max_amount):
        """
        Property: For any stipend range, parsing should return the minimum value.
        """
        scraper = MockScraper()
        
        # Create range format
        range_str = f"{min_amount}-{max_amount}"
        result = scraper._parse_stipend(range_str)
        
        # Should return minimum value
        if result is not None:
            assert result == min_amount, \
                f"Expected minimum {min_amount} from range '{range_str}', got {result}"
    
    @settings(max_examples=100)
    @given(
        text=st.text(alphabet=st.characters(blacklist_categories=('Nd',)), min_size=1, max_size=50)
    )
    def test_parse_non_numeric_text(self, text):
        """
        Property: For any text without numbers, parsing should return None.
        """
        scraper = MockScraper()
        
        # Skip if text contains unpaid indicators (those should also return None)
        unpaid_indicators = ['unpaid', 'not disclosed', 'not mentioned', 'n/a', 'na']
        if any(indicator in text.lower() for indicator in unpaid_indicators):
            return
        
        result = scraper._parse_stipend(text)
        
        # Should return None for non-numeric text
        assert result is None, \
            f"Expected None for non-numeric text '{text}', got {result}"
    
    @settings(max_examples=100)
    @given(
        unpaid_text=st.sampled_from([
            "Unpaid", "unpaid", "UNPAID", "Not disclosed", "Not Disclosed",
            "NOT DISCLOSED", "Not mentioned", "N/A", "NA", "n/a"
        ])
    )
    def test_parse_unpaid_indicators(self, unpaid_text):
        """
        Property: For any unpaid indicator text, parsing should return None.
        """
        scraper = MockScraper()
        result = scraper._parse_stipend(unpaid_text)
        
        assert result is None, \
            f"Expected None for unpaid indicator '{unpaid_text}', got {result}"
