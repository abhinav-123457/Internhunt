"""
Unit Tests for Deduplicator

Tests specific functionality and edge cases for the deduplicator module.
"""

import pytest

from src.deduplicator import Deduplicator
from src.scoring_engine import ScoredListing
from src.scrapers.base_scraper import JobListing


class TestTextNormalization:
    """Test text normalization functionality"""
    
    def test_normalize_lowercase(self):
        """Test that text is converted to lowercase"""
        assert Deduplicator.normalize_text("HELLO WORLD") == "hello world"
        assert Deduplicator.normalize_text("MiXeD CaSe") == "mixed case"
    
    def test_normalize_strip_whitespace(self):
        """Test that leading/trailing whitespace is removed"""
        assert Deduplicator.normalize_text("  hello  ") == "hello"
        assert Deduplicator.normalize_text("\t\nhello\n\t") == "hello"
    
    def test_normalize_remove_special_chars(self):
        """Test that special characters are removed (underscores are kept as word characters)"""
        assert Deduplicator.normalize_text("hello@world!") == "helloworld"
        assert Deduplicator.normalize_text("test-123_abc") == "test123_abc"  # underscore is kept
        assert Deduplicator.normalize_text("a.b,c;d:e") == "abcde"
    
    def test_normalize_collapse_spaces(self):
        """Test that multiple spaces are collapsed to single space"""
        assert Deduplicator.normalize_text("hello    world") == "hello world"
        assert Deduplicator.normalize_text("a  b  c") == "a b c"
    
    def test_normalize_empty_string(self):
        """Test normalization of empty string"""
        assert Deduplicator.normalize_text("") == ""
        assert Deduplicator.normalize_text("   ") == ""
    
    def test_normalize_combined(self):
        """Test normalization with multiple transformations"""
        assert Deduplicator.normalize_text("  HELLO,  World!  ") == "hello world"
        assert Deduplicator.normalize_text("Test@123  -  ABC") == "test123 abc"


class TestDeduplicationExactDuplicates:
    """Test deduplication with exact duplicates"""
    
    def test_exact_duplicates_removed(self):
        """Test that exact duplicates are removed"""
        # Create two identical listings with different scores
        listing1 = ScoredListing(
            listing=JobListing(
                title="ML Intern",
                company="TechCorp",
                stipend=20000,
                location="Bangalore",
                description="Machine learning internship",
                url="http://test.com/1",
                posted_date="2024-01-01",
                source_platform="Test",
                raw_stipend_text="20000"
            ),
            score=15.0,
            score_breakdown={'keyword': 4.0, 'skill': 3.0, 'stipend': 5.0, 'remote': 0.0, 'location': 3.0}
        )
        
        listing2 = ScoredListing(
            listing=JobListing(
                title="ML Intern",
                company="TechCorp",
                stipend=18000,
                location="Remote",
                description="Different description",
                url="http://test.com/2",
                posted_date="2024-01-02",
                source_platform="Test",
                raw_stipend_text="18000"
            ),
            score=10.0,
            score_breakdown={'keyword': 2.0, 'skill': 3.0, 'stipend': 3.0, 'remote': 0.0, 'location': 2.0}
        )
        
        deduplicated = Deduplicator.deduplicate([listing1, listing2])
        
        assert len(deduplicated) == 1
        assert deduplicated[0].score == 15.0  # Higher score retained
    
    def test_three_duplicates(self):
        """Test deduplication with three duplicates"""
        listings = []
        for i, score in enumerate([10.0, 25.0, 15.0]):
            listing = ScoredListing(
                listing=JobListing(
                    title="Data Analyst",
                    company="DataCo",
                    stipend=15000,
                    location="Mumbai",
                    description=f"Description {i}",
                    url=f"http://test.com/{i}",
                    posted_date="2024-01-01",
                    source_platform="Test",
                    raw_stipend_text="15000"
                ),
                score=score,
                score_breakdown={'keyword': score/5, 'skill': score/5, 'stipend': score/5, 'remote': score/5, 'location': score/5}
            )
            listings.append(listing)
        
        deduplicated = Deduplicator.deduplicate(listings)
        
        assert len(deduplicated) == 1
        assert deduplicated[0].score == 25.0  # Highest score retained


class TestDeduplicationCaseVariations:
    """Test deduplication with case variations"""
    
    def test_case_variations_deduplicated(self):
        """Test that case variations are treated as duplicates"""
        listings = [
            ScoredListing(
                listing=JobListing(
                    title="Python Developer",
                    company="CodeCorp",
                    stipend=25000,
                    location="Delhi",
                    description="Python development",
                    url="http://test.com/1",
                    posted_date="2024-01-01",
                    source_platform="Test",
                    raw_stipend_text="25000"
                ),
                score=20.0,
                score_breakdown={'keyword': 4.0, 'skill': 4.0, 'stipend': 5.0, 'remote': 4.0, 'location': 3.0}
            ),
            ScoredListing(
                listing=JobListing(
                    title="PYTHON DEVELOPER",
                    company="CODECORP",
                    stipend=22000,
                    location="Delhi",
                    description="Python development",
                    url="http://test.com/2",
                    posted_date="2024-01-02",
                    source_platform="Test",
                    raw_stipend_text="22000"
                ),
                score=18.0,
                score_breakdown={'keyword': 4.0, 'skill': 3.0, 'stipend': 4.0, 'remote': 4.0, 'location': 3.0}
            ),
            ScoredListing(
                listing=JobListing(
                    title="python developer",
                    company="codecorp",
                    stipend=20000,
                    location="Delhi",
                    description="Python development",
                    url="http://test.com/3",
                    posted_date="2024-01-03",
                    source_platform="Test",
                    raw_stipend_text="20000"
                ),
                score=16.0,
                score_breakdown={'keyword': 4.0, 'skill': 2.0, 'stipend': 3.0, 'remote': 4.0, 'location': 3.0}
            )
        ]
        
        deduplicated = Deduplicator.deduplicate(listings)
        
        assert len(deduplicated) == 1
        assert deduplicated[0].score == 20.0  # Highest score retained


class TestDeduplicationWhitespaceVariations:
    """Test deduplication with whitespace variations"""
    
    def test_whitespace_variations_deduplicated(self):
        """Test that whitespace variations are treated as duplicates"""
        listings = [
            ScoredListing(
                listing=JobListing(
                    title="Web Developer",
                    company="WebCo",
                    stipend=30000,
                    location="Pune",
                    description="Web development",
                    url="http://test.com/1",
                    posted_date="2024-01-01",
                    source_platform="Test",
                    raw_stipend_text="30000"
                ),
                score=25.0,
                score_breakdown={'keyword': 5.0, 'skill': 5.0, 'stipend': 5.0, 'remote': 5.0, 'location': 5.0}
            ),
            ScoredListing(
                listing=JobListing(
                    title="  Web   Developer  ",
                    company="  WebCo  ",
                    stipend=28000,
                    location="Pune",
                    description="Web development",
                    url="http://test.com/2",
                    posted_date="2024-01-02",
                    source_platform="Test",
                    raw_stipend_text="28000"
                ),
                score=22.0,
                score_breakdown={'keyword': 4.0, 'skill': 5.0, 'stipend': 4.0, 'remote': 5.0, 'location': 4.0}
            ),
            ScoredListing(
                listing=JobListing(
                    title="\tWeb\tDeveloper\n",
                    company="\nWebCo\t",
                    stipend=26000,
                    location="Pune",
                    description="Web development",
                    url="http://test.com/3",
                    posted_date="2024-01-03",
                    source_platform="Test",
                    raw_stipend_text="26000"
                ),
                score=20.0,
                score_breakdown={'keyword': 4.0, 'skill': 4.0, 'stipend': 4.0, 'remote': 5.0, 'location': 3.0}
            )
        ]
        
        deduplicated = Deduplicator.deduplicate(listings)
        
        assert len(deduplicated) == 1
        assert deduplicated[0].score == 25.0  # Highest score retained


class TestDeduplicationOrderPreservation:
    """Test that deduplication preserves sorted order"""
    
    def test_order_preserved_after_deduplication(self):
        """Test that sorted order is maintained after deduplication"""
        # Create listings with different titles/companies, already sorted by score
        listings = [
            ScoredListing(
                listing=JobListing(
                    title="Job A",
                    company="Company A",
                    stipend=30000,
                    location="City A",
                    description="Description A",
                    url="http://test.com/a",
                    posted_date="2024-01-01",
                    source_platform="Test",
                    raw_stipend_text="30000"
                ),
                score=30.0,
                score_breakdown={'keyword': 6.0, 'skill': 6.0, 'stipend': 6.0, 'remote': 6.0, 'location': 6.0}
            ),
            ScoredListing(
                listing=JobListing(
                    title="Job B",
                    company="Company B",
                    stipend=25000,
                    location="City B",
                    description="Description B",
                    url="http://test.com/b",
                    posted_date="2024-01-02",
                    source_platform="Test",
                    raw_stipend_text="25000"
                ),
                score=25.0,
                score_breakdown={'keyword': 5.0, 'skill': 5.0, 'stipend': 5.0, 'remote': 5.0, 'location': 5.0}
            ),
            ScoredListing(
                listing=JobListing(
                    title="Job C",
                    company="Company C",
                    stipend=20000,
                    location="City C",
                    description="Description C",
                    url="http://test.com/c",
                    posted_date="2024-01-03",
                    source_platform="Test",
                    raw_stipend_text="20000"
                ),
                score=20.0,
                score_breakdown={'keyword': 4.0, 'skill': 4.0, 'stipend': 4.0, 'remote': 4.0, 'location': 4.0}
            )
        ]
        
        deduplicated = Deduplicator.deduplicate(listings)
        
        # All should be retained (no duplicates)
        assert len(deduplicated) == 3
        
        # Order should be preserved (descending by score)
        assert deduplicated[0].score == 30.0
        assert deduplicated[1].score == 25.0
        assert deduplicated[2].score == 20.0
    
    def test_order_preserved_with_duplicates(self):
        """Test that order is preserved when duplicates are removed"""
        listings = [
            # Highest score unique listing
            ScoredListing(
                listing=JobListing(
                    title="Unique Job",
                    company="Unique Co",
                    stipend=35000,
                    location="City",
                    description="Description",
                    url="http://test.com/1",
                    posted_date="2024-01-01",
                    source_platform="Test",
                    raw_stipend_text="35000"
                ),
                score=35.0,
                score_breakdown={'keyword': 7.0, 'skill': 7.0, 'stipend': 7.0, 'remote': 7.0, 'location': 7.0}
            ),
            # Duplicate group (higher score)
            ScoredListing(
                listing=JobListing(
                    title="Duplicate Job",
                    company="Duplicate Co",
                    stipend=30000,
                    location="City",
                    description="Description",
                    url="http://test.com/2",
                    posted_date="2024-01-02",
                    source_platform="Test",
                    raw_stipend_text="30000"
                ),
                score=30.0,
                score_breakdown={'keyword': 6.0, 'skill': 6.0, 'stipend': 6.0, 'remote': 6.0, 'location': 6.0}
            ),
            # Another unique listing
            ScoredListing(
                listing=JobListing(
                    title="Another Job",
                    company="Another Co",
                    stipend=25000,
                    location="City",
                    description="Description",
                    url="http://test.com/3",
                    posted_date="2024-01-03",
                    source_platform="Test",
                    raw_stipend_text="25000"
                ),
                score=25.0,
                score_breakdown={'keyword': 5.0, 'skill': 5.0, 'stipend': 5.0, 'remote': 5.0, 'location': 5.0}
            ),
            # Duplicate group (lower score - should be removed)
            ScoredListing(
                listing=JobListing(
                    title="Duplicate Job",
                    company="Duplicate Co",
                    stipend=20000,
                    location="City",
                    description="Different description",
                    url="http://test.com/4",
                    posted_date="2024-01-04",
                    source_platform="Test",
                    raw_stipend_text="20000"
                ),
                score=20.0,
                score_breakdown={'keyword': 4.0, 'skill': 4.0, 'stipend': 4.0, 'remote': 4.0, 'location': 4.0}
            )
        ]
        
        deduplicated = Deduplicator.deduplicate(listings)
        
        # Should have 3 unique listings
        assert len(deduplicated) == 3
        
        # Order should be preserved
        assert deduplicated[0].score == 35.0
        assert deduplicated[0].listing.title == "Unique Job"
        
        assert deduplicated[1].score == 30.0
        assert deduplicated[1].listing.title == "Duplicate Job"
        
        assert deduplicated[2].score == 25.0
        assert deduplicated[2].listing.title == "Another Job"


class TestDeduplicationEdgeCases:
    """Test edge cases for deduplication"""
    
    def test_empty_list(self):
        """Test deduplication of empty list"""
        deduplicated = Deduplicator.deduplicate([])
        assert deduplicated == []
    
    def test_single_listing(self):
        """Test deduplication with single listing"""
        listing = ScoredListing(
            listing=JobListing(
                title="Single Job",
                company="Single Co",
                stipend=20000,
                location="City",
                description="Description",
                url="http://test.com",
                posted_date="2024-01-01",
                source_platform="Test",
                raw_stipend_text="20000"
            ),
            score=20.0,
            score_breakdown={'keyword': 4.0, 'skill': 4.0, 'stipend': 4.0, 'remote': 4.0, 'location': 4.0}
        )
        
        deduplicated = Deduplicator.deduplicate([listing])
        
        assert len(deduplicated) == 1
        assert deduplicated[0] == listing
    
    def test_all_unique(self):
        """Test deduplication when all listings are unique"""
        listings = []
        for i in range(5):
            listing = ScoredListing(
                listing=JobListing(
                    title=f"Job {i}",
                    company=f"Company {i}",
                    stipend=20000 + i * 1000,
                    location="City",
                    description="Description",
                    url=f"http://test.com/{i}",
                    posted_date="2024-01-01",
                    source_platform="Test",
                    raw_stipend_text=str(20000 + i * 1000)
                ),
                score=20.0 + i,
                score_breakdown={'keyword': 4.0, 'skill': 4.0, 'stipend': 4.0, 'remote': 4.0, 'location': 4.0}
            )
            listings.append(listing)
        
        deduplicated = Deduplicator.deduplicate(listings)
        
        # All should be retained
        assert len(deduplicated) == 5
    
    def test_all_duplicates(self):
        """Test deduplication when all listings are duplicates"""
        listings = []
        for i in range(5):
            listing = ScoredListing(
                listing=JobListing(
                    title="Same Job",
                    company="Same Company",
                    stipend=20000 + i * 1000,
                    location="City",
                    description=f"Description {i}",
                    url=f"http://test.com/{i}",
                    posted_date="2024-01-01",
                    source_platform="Test",
                    raw_stipend_text=str(20000 + i * 1000)
                ),
                score=20.0 + i,
                score_breakdown={'keyword': 4.0, 'skill': 4.0, 'stipend': 4.0, 'remote': 4.0, 'location': 4.0}
            )
            listings.append(listing)
        
        deduplicated = Deduplicator.deduplicate(listings)
        
        # Only one should be retained (highest score)
        assert len(deduplicated) == 1
        assert deduplicated[0].score == 24.0  # 20.0 + 4
