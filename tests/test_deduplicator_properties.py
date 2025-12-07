"""
Property-Based Tests for Deduplicator

Tests universal properties that should hold across all inputs using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from src.deduplicator import Deduplicator
from src.scoring_engine import ScoredListing
from src.scrapers.base_scraper import JobListing


# Strategy for generating job listings
@st.composite
def job_listing_strategy(draw, title=None, company=None):
    """Generate random JobListing objects"""
    title = title if title is not None else draw(st.text(min_size=1, max_size=100))
    company = company if company is not None else draw(st.text(min_size=1, max_size=50))
    stipend = draw(st.one_of(st.none(), st.integers(min_value=0, max_value=100000)))
    location = draw(st.text(min_size=1, max_size=50))
    description = draw(st.text(min_size=0, max_size=500))
    url = draw(st.text(min_size=10, max_size=100))
    posted_date = draw(st.one_of(st.none(), st.text(min_size=1, max_size=20)))
    source_platform = draw(st.sampled_from(['Internshala', 'Unstop', 'Naukri', 'LinkedIn', 'LetsIntern', 'InternWorld']))
    raw_stipend_text = draw(st.text(min_size=0, max_size=50))
    
    return JobListing(
        title=title,
        company=company,
        stipend=stipend,
        location=location,
        description=description,
        url=url,
        posted_date=posted_date,
        source_platform=source_platform,
        raw_stipend_text=raw_stipend_text
    )


# Strategy for generating scored listings
@st.composite
def scored_listing_strategy(draw, title=None, company=None, score=None):
    """Generate random ScoredListing objects"""
    listing = draw(job_listing_strategy(title=title, company=company))
    score = score if score is not None else draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    score_breakdown = {
        'keyword': draw(st.floats(min_value=0.0, max_value=20.0, allow_nan=False, allow_infinity=False)),
        'skill': draw(st.floats(min_value=0.0, max_value=20.0, allow_nan=False, allow_infinity=False)),
        'stipend': draw(st.floats(min_value=0.0, max_value=5.0, allow_nan=False, allow_infinity=False)),
        'remote': draw(st.floats(min_value=0.0, max_value=5.0, allow_nan=False, allow_infinity=False)),
        'location': draw(st.floats(min_value=0.0, max_value=3.0, allow_nan=False, allow_infinity=False))
    }
    
    return ScoredListing(
        listing=listing,
        score=score,
        score_breakdown=score_breakdown
    )


class TestDeduplicationKeyUniqueness:
    """
    Property 9: Deduplication key uniqueness
    
    For any two listings with identical normalized title and company name,
    only one should appear in the deduplicated results.
    
    Validates: Requirements 5.1, 5.2
    """
    
    @settings(max_examples=100)
    @given(
        base_title=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'P'))),
        base_company=st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=('L', 'N', 'P'))),
        num_duplicates=st.integers(min_value=2, max_value=10),
        data=st.data()
    )
    def test_identical_title_company_deduplicated(self, base_title, base_company, num_duplicates, data):
        """
        **Feature: internhunt-v6, Property 9: Deduplication key uniqueness**
        **Validates: Requirements 5.1, 5.2**
        
        Test that listings with identical normalized title and company appear only once.
        """
        # Ensure base title and company are not empty after normalization
        assume(len(base_title.strip()) >= 3)
        assume(len(base_company.strip()) >= 3)
        
        # Create multiple listings with same title and company but different scores
        listings = []
        for i in range(num_duplicates):
            score = data.draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
            listing = data.draw(scored_listing_strategy(title=base_title, company=base_company, score=score))
            listings.append(listing)
        
        # Deduplicate
        deduplicated = Deduplicator.deduplicate(listings)
        
        # Should have exactly 1 listing
        assert len(deduplicated) == 1, \
            f"Expected 1 unique listing after deduplication, got {len(deduplicated)}"
    
    @settings(max_examples=100)
    @given(
        base_title=st.text(min_size=3, max_size=50, alphabet=st.characters(min_codepoint=65, max_codepoint=122)),
        base_company=st.text(min_size=3, max_size=30, alphabet=st.characters(min_codepoint=65, max_codepoint=122)),
        case_variations=st.lists(
            st.sampled_from(['lower', 'upper', 'title', 'mixed']),
            min_size=2,
            max_size=5
        ),
        data=st.data()
    )
    def test_case_variations_deduplicated(self, base_title, base_company, case_variations, data):
        """
        **Feature: internhunt-v6, Property 9: Deduplication key uniqueness**
        **Validates: Requirements 5.1, 5.2**
        
        Test that case variations of same title/company are deduplicated.
        Uses ASCII characters only to avoid Unicode case-folding edge cases.
        """
        # Ensure base strings are not empty and contain letters
        assume(len(base_title.strip()) >= 3)
        assume(len(base_company.strip()) >= 3)
        assume(any(c.isalpha() for c in base_title))
        assume(any(c.isalpha() for c in base_company))
        
        # Create listings with different case variations
        listings = []
        for variation in case_variations:
            if variation == 'lower':
                title = base_title.lower()
                company = base_company.lower()
            elif variation == 'upper':
                title = base_title.upper()
                company = base_company.upper()
            elif variation == 'title':
                title = base_title.title()
                company = base_company.title()
            else:  # mixed
                title = ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(base_title))
                company = ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(base_company))
            
            score = data.draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
            listing = data.draw(scored_listing_strategy(title=title, company=company, score=score))
            listings.append(listing)
        
        # Deduplicate
        deduplicated = Deduplicator.deduplicate(listings)
        
        # Should have exactly 1 listing (all case variations should be treated as same)
        assert len(deduplicated) == 1, \
            f"Expected 1 unique listing after deduplication of case variations, got {len(deduplicated)}"
    
    @settings(max_examples=100)
    @given(
        base_title=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        base_company=st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        num_duplicates=st.integers(min_value=2, max_value=5),
        data=st.data()
    )
    def test_whitespace_variations_deduplicated(self, base_title, base_company, num_duplicates, data):
        """
        **Feature: internhunt-v6, Property 9: Deduplication key uniqueness**
        **Validates: Requirements 5.1, 5.2**
        
        Test that whitespace variations are deduplicated.
        """
        # Ensure base strings are not empty
        assume(len(base_title.strip()) >= 3)
        assume(len(base_company.strip()) >= 3)
        
        # Create listings with different whitespace variations
        listings = []
        whitespace_variations = [
            lambda s: s,  # original
            lambda s: f"  {s}  ",  # leading/trailing spaces
            lambda s: s.replace(' ', '  '),  # double spaces
            lambda s: f"\t{s}\n",  # tabs and newlines
            lambda s: '  '.join(s.split())  # multiple spaces between words
        ]
        
        for i in range(min(num_duplicates, len(whitespace_variations))):
            variation_func = whitespace_variations[i]
            title = variation_func(base_title)
            company = variation_func(base_company)
            
            score = data.draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
            listing = data.draw(scored_listing_strategy(title=title, company=company, score=score))
            listings.append(listing)
        
        # Deduplicate
        deduplicated = Deduplicator.deduplicate(listings)
        
        # Should have exactly 1 listing (all whitespace variations should be treated as same)
        assert len(deduplicated) == 1, \
            f"Expected 1 unique listing after deduplication of whitespace variations, got {len(deduplicated)}"
    
    @settings(max_examples=100)
    @given(
        listings=st.lists(scored_listing_strategy(), min_size=1, max_size=50)
    )
    def test_deduplicate_returns_unique_keys(self, listings):
        """
        **Feature: internhunt-v6, Property 9: Deduplication key uniqueness**
        **Validates: Requirements 5.1, 5.2**
        
        Test that deduplicate returns only unique title+company combinations.
        """
        # Deduplicate
        deduplicated = Deduplicator.deduplicate(listings)
        
        # Generate keys for all deduplicated listings
        keys = [Deduplicator._generate_key(listing) for listing in deduplicated]
        
        # All keys should be unique
        assert len(keys) == len(set(keys)), \
            f"Deduplicated results should have unique keys, found {len(keys)} listings but {len(set(keys))} unique keys"


class TestDeduplicationPreservesHighestScore:
    """
    Property 10: Deduplication preserves highest score
    
    For any set of duplicate listings, the deduplicated result should contain
    the listing with the highest score among the duplicates.
    
    Validates: Requirements 5.2
    """
    
    @settings(max_examples=100)
    @given(
        base_title=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        base_company=st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        scores=st.lists(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False), min_size=2, max_size=10),
        data=st.data()
    )
    def test_highest_score_retained(self, base_title, base_company, scores, data):
        """
        **Feature: internhunt-v6, Property 10: Deduplication preserves highest score**
        **Validates: Requirements 5.2**
        
        Test that the listing with highest score is retained among duplicates.
        """
        # Ensure base strings are not empty
        assume(len(base_title.strip()) >= 3)
        assume(len(base_company.strip()) >= 3)
        
        # Ensure we have at least 2 different scores
        assume(len(set(scores)) >= 2)
        
        # Create listings with same title/company but different scores
        listings = []
        for score in scores:
            listing = data.draw(scored_listing_strategy(title=base_title, company=base_company, score=score))
            listings.append(listing)
        
        # Find the maximum score
        max_score = max(scores)
        
        # Deduplicate
        deduplicated = Deduplicator.deduplicate(listings)
        
        # Should have exactly 1 listing
        assert len(deduplicated) == 1, \
            f"Expected 1 listing after deduplication, got {len(deduplicated)}"
        
        # The retained listing should have the maximum score
        assert deduplicated[0].score == max_score, \
            f"Expected highest score {max_score} to be retained, got {deduplicated[0].score}"
    
    @settings(max_examples=100)
    @given(
        num_groups=st.integers(min_value=2, max_value=10),
        duplicates_per_group=st.integers(min_value=2, max_value=5),
        data=st.data()
    )
    def test_highest_score_retained_multiple_groups(self, num_groups, duplicates_per_group, data):
        """
        **Feature: internhunt-v6, Property 10: Deduplication preserves highest score**
        **Validates: Requirements 5.2**
        
        Test that highest scores are retained for multiple duplicate groups.
        """
        listings = []
        expected_max_scores = {}
        
        # Create multiple groups of duplicates
        for group_idx in range(num_groups):
            title = f"Title{group_idx}"
            company = f"Company{group_idx}"
            
            group_scores = []
            for dup_idx in range(duplicates_per_group):
                score = data.draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
                group_scores.append(score)
                listing = data.draw(scored_listing_strategy(title=title, company=company, score=score))
                listings.append(listing)
            
            # Track the maximum score for this group
            key = Deduplicator.normalize_text(title) + "::" + Deduplicator.normalize_text(company)
            expected_max_scores[key] = max(group_scores)
        
        # Deduplicate
        deduplicated = Deduplicator.deduplicate(listings)
        
        # Should have exactly num_groups listings
        assert len(deduplicated) == num_groups, \
            f"Expected {num_groups} unique listings after deduplication, got {len(deduplicated)}"
        
        # Each deduplicated listing should have the maximum score for its group
        for listing in deduplicated:
            key = Deduplicator._generate_key(listing)
            expected_score = expected_max_scores[key]
            assert listing.score == expected_score, \
                f"Expected score {expected_score} for key '{key}', got {listing.score}"
    
    @settings(max_examples=100)
    @given(
        listings=st.lists(scored_listing_strategy(), min_size=2, max_size=30)
    )
    def test_no_score_degradation(self, listings):
        """
        **Feature: internhunt-v6, Property 10: Deduplication preserves highest score**
        **Validates: Requirements 5.2**
        
        Test that deduplication never results in a lower score for any key.
        """
        # Create a mapping of keys to maximum scores before deduplication
        key_to_max_score = {}
        for listing in listings:
            key = Deduplicator._generate_key(listing)
            if key not in key_to_max_score:
                key_to_max_score[key] = listing.score
            else:
                key_to_max_score[key] = max(key_to_max_score[key], listing.score)
        
        # Deduplicate
        deduplicated = Deduplicator.deduplicate(listings)
        
        # Check that each deduplicated listing has the maximum score for its key
        for listing in deduplicated:
            key = Deduplicator._generate_key(listing)
            expected_max = key_to_max_score[key]
            assert listing.score == expected_max, \
                f"Deduplication should preserve highest score for key '{key}': expected {expected_max}, got {listing.score}"
