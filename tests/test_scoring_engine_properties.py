"""
Property-Based Tests for Scoring Engine

Tests universal properties that should hold across all inputs using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from src.scoring_engine import ScoringEngine, ScoredListing
from src.scrapers.base_scraper import JobListing
from src.preference_wizard import UserPreferences


# Strategy for generating job listings
@st.composite
def job_listing_strategy(draw):
    """Generate random JobListing objects"""
    title = draw(st.text(min_size=1, max_size=100))
    company = draw(st.text(min_size=1, max_size=50))
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


# Strategy for generating user preferences
@st.composite
def user_preferences_strategy(draw, wanted_kw=None, reject_kw=None, remote_pref=None, min_stip=None):
    """Generate random UserPreferences objects"""
    wanted_keywords = wanted_kw if wanted_kw is not None else draw(st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10))
    reject_keywords = reject_kw if reject_kw is not None else draw(st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10))
    remote_preference = remote_pref if remote_pref is not None else draw(st.sampled_from(['yes', 'no', 'any']))
    min_stipend = min_stip if min_stip is not None else draw(st.integers(min_value=0, max_value=50000))
    max_post_age_days = draw(st.integers(min_value=1, max_value=365))
    max_results = draw(st.integers(min_value=1, max_value=200))
    preferred_locations = draw(st.lists(st.text(min_size=1, max_size=30), min_size=0, max_size=5))
    resume_skills = draw(st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=20))
    
    return UserPreferences(
        wanted_keywords=wanted_keywords,
        reject_keywords=reject_keywords,
        remote_preference=remote_preference,
        min_stipend=min_stipend,
        max_post_age_days=max_post_age_days,
        max_results=max_results,
        preferred_locations=preferred_locations,
        resume_skills=resume_skills
    )


class TestRejectKeywordFiltering:
    """
    Property 4: Reject keyword filtering
    
    For any listing containing a reject keyword in its title or description,
    that listing should not appear in the final scored results.
    
    Validates: Requirements 4.7
    """
    
    @settings(max_examples=100)
    @given(
        reject_keyword=st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        other_text=st.text(min_size=0, max_size=100),
        preferences_data=st.data()
    )
    def test_reject_keyword_in_title_excludes_listing(self, reject_keyword, other_text, preferences_data):
        """
        **Feature: internhunt-v6, Property 4: Reject keyword filtering**
        **Validates: Requirements 4.7**
        
        Test that listings with reject keywords in title are excluded.
        """
        # Ensure reject keyword is not empty after normalization
        reject_keyword = reject_keyword.strip().lower()
        assume(len(reject_keyword) >= 3)
        
        # Create preferences with the reject keyword
        preferences = preferences_data.draw(user_preferences_strategy(reject_kw=[reject_keyword]))
        
        # Create listing with reject keyword in title
        listing = JobListing(
            title=f"{other_text} {reject_keyword} {other_text}",
            company="Test Company",
            stipend=10000,
            location="Test Location",
            description="Test description",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="10000"
        )
        
        # Score the listing
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        # Listing should be rejected (None)
        assert result is None, f"Listing with reject keyword '{reject_keyword}' in title should be rejected"
    
    @settings(max_examples=100)
    @given(
        reject_keyword=st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        other_text=st.text(min_size=0, max_size=100),
        preferences_data=st.data()
    )
    def test_reject_keyword_in_description_excludes_listing(self, reject_keyword, other_text, preferences_data):
        """
        **Feature: internhunt-v6, Property 4: Reject keyword filtering**
        **Validates: Requirements 4.7**
        
        Test that listings with reject keywords in description are excluded.
        """
        # Ensure reject keyword is not empty after normalization
        reject_keyword = reject_keyword.strip().lower()
        assume(len(reject_keyword) >= 3)
        
        # Create preferences with the reject keyword
        preferences = preferences_data.draw(user_preferences_strategy(reject_kw=[reject_keyword]))
        
        # Create listing with reject keyword in description
        listing = JobListing(
            title="Test Title",
            company="Test Company",
            stipend=10000,
            location="Test Location",
            description=f"{other_text} {reject_keyword} {other_text}",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="10000"
        )
        
        # Score the listing
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        # Listing should be rejected (None)
        assert result is None, f"Listing with reject keyword '{reject_keyword}' in description should be rejected"
    
    @settings(max_examples=100)
    @given(
        listings=st.lists(job_listing_strategy(), min_size=1, max_size=20),
        reject_keyword=st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        preferences_data=st.data()
    )
    def test_score_all_excludes_rejected_listings(self, listings, reject_keyword, preferences_data):
        """
        **Feature: internhunt-v6, Property 4: Reject keyword filtering**
        **Validates: Requirements 4.7**
        
        Test that score_all excludes all listings with reject keywords.
        """
        reject_keyword = reject_keyword.strip().lower()
        assume(len(reject_keyword) >= 3)
        
        # Create preferences with the reject keyword
        preferences = preferences_data.draw(user_preferences_strategy(reject_kw=[reject_keyword]))
        
        # Score all listings
        engine = ScoringEngine(preferences)
        scored = engine.score_all(listings)
        
        # Check that no scored listing contains the reject keyword
        for scored_listing in scored:
            searchable_text = f"{scored_listing.listing.title} {scored_listing.listing.description}".lower()
            assert reject_keyword not in searchable_text, \
                f"Scored listing should not contain reject keyword '{reject_keyword}'"


class TestWantedKeywordScoringConsistency:
    """
    Property 5: Wanted keyword scoring consistency
    
    For any listing, the number of wanted keyword matches multiplied by 2
    should equal the keyword component of the total score.
    
    Validates: Requirements 4.1
    """
    
    @settings(max_examples=100)
    @given(
        wanted_keywords=st.lists(st.text(min_size=3, max_size=15, alphabet=st.characters(whitelist_categories=('L',))), min_size=1, max_size=10),
        listing=job_listing_strategy(),
        preferences_data=st.data()
    )
    def test_keyword_score_equals_matches_times_two(self, wanted_keywords, listing, preferences_data):
        """
        **Feature: internhunt-v6, Property 5: Wanted keyword scoring consistency**
        **Validates: Requirements 4.1**
        
        Test that keyword score equals (matches * 2).
        """
        # Normalize keywords
        wanted_keywords = [kw.strip().lower() for kw in wanted_keywords if kw.strip()]
        assume(len(wanted_keywords) > 0)
        
        # Create preferences
        preferences = preferences_data.draw(user_preferences_strategy(wanted_kw=wanted_keywords, reject_kw=[]))
        
        # Score the listing
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        # If listing was rejected for other reasons, skip
        assume(result is not None)
        
        # Count actual keyword matches
        searchable_text = f"{listing.title} {listing.description}".lower()
        actual_matches = sum(1 for kw in wanted_keywords if kw in searchable_text)
        
        # Verify keyword score
        expected_keyword_score = actual_matches * 2.0
        assert result.score_breakdown['keyword'] == expected_keyword_score, \
            f"Keyword score should be {expected_keyword_score} (matches={actual_matches}), got {result.score_breakdown['keyword']}"


class TestRemoteDetectionAccuracy:
    """
    Property 6: Remote detection accuracy
    
    For any listing containing remote work indicators in location or description,
    the remote detection should identify it using case-insensitive regex matching.
    
    Validates: Requirements 4.4, 10.1, 10.2, 10.3
    """
    
    @settings(max_examples=100)
    @given(
        remote_indicator=st.sampled_from(['remote', 'wfh', 'work from home', 'work-from-home', 'pan india', 'pan-india', 'anywhere in india']),
        location_or_desc=st.sampled_from(['location', 'description']),
        other_text=st.text(min_size=0, max_size=50),
        preferences_data=st.data()
    )
    def test_remote_indicators_detected(self, remote_indicator, location_or_desc, other_text, preferences_data):
        """
        **Feature: internhunt-v6, Property 6: Remote detection accuracy**
        **Validates: Requirements 4.4, 10.1, 10.2, 10.3**
        
        Test that remote indicators are detected in location or description.
        """
        # Create preferences with remote preference = 'yes'
        preferences = preferences_data.draw(user_preferences_strategy(remote_pref='yes', reject_kw=[]))
        
        # Create listing with remote indicator
        if location_or_desc == 'location':
            listing = JobListing(
                title="Test Title",
                company="Test Company",
                stipend=10000,
                location=f"{other_text} {remote_indicator} {other_text}",
                description="Test description",
                url="http://test.com",
                posted_date="2024-01-01",
                source_platform="Test",
                raw_stipend_text="10000"
            )
        else:
            listing = JobListing(
                title="Test Title",
                company="Test Company",
                stipend=10000,
                location="Test Location",
                description=f"{other_text} {remote_indicator} {other_text}",
                url="http://test.com",
                posted_date="2024-01-01",
                source_platform="Test",
                raw_stipend_text="10000"
            )
        
        # Score the listing
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        # If listing was rejected for other reasons, skip
        assume(result is not None)
        
        # Remote score should be 5.0
        assert result.score_breakdown['remote'] == 5.0, \
            f"Remote indicator '{remote_indicator}' should be detected and score 5.0, got {result.score_breakdown['remote']}"
    
    @settings(max_examples=100)
    @given(
        remote_indicator=st.sampled_from(['REMOTE', 'WFH', 'Work From Home', 'WORK-FROM-HOME', 'Pan India', 'PAN-INDIA']),
        preferences_data=st.data()
    )
    def test_remote_detection_case_insensitive(self, remote_indicator, preferences_data):
        """
        **Feature: internhunt-v6, Property 6: Remote detection accuracy**
        **Validates: Requirements 4.4, 10.1, 10.2, 10.3**
        
        Test that remote detection is case-insensitive.
        """
        # Create preferences with remote preference = 'yes'
        preferences = preferences_data.draw(user_preferences_strategy(remote_pref='yes', reject_kw=[]))
        
        # Create listing with uppercase/mixed case remote indicator
        listing = JobListing(
            title="Test Title",
            company="Test Company",
            stipend=10000,
            location=remote_indicator,
            description="Test description",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="10000"
        )
        
        # Score the listing
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        # If listing was rejected for other reasons, skip
        assume(result is not None)
        
        # Remote score should be 5.0
        assert result.score_breakdown['remote'] == 5.0, \
            f"Remote indicator '{remote_indicator}' should be detected (case-insensitive), got {result.score_breakdown['remote']}"


class TestStipendScoringMonotonicity:
    """
    Property 7: Stipend scoring monotonicity
    
    For any two listings with stipends S1 and S2 where S1 > S2,
    the stipend score component for the first listing should be
    greater than or equal to the second listing's stipend score.
    
    Validates: Requirements 4.3
    """
    
    @settings(max_examples=100)
    @given(
        stipend1=st.integers(min_value=1000, max_value=100000),
        stipend2=st.integers(min_value=1000, max_value=100000),
        preferences_data=st.data()
    )
    def test_higher_stipend_gets_higher_or_equal_score(self, stipend1, stipend2, preferences_data):
        """
        **Feature: internhunt-v6, Property 7: Stipend scoring monotonicity**
        **Validates: Requirements 4.3**
        
        Test that higher stipends receive higher or equal scores.
        """
        # Ensure stipend1 > stipend2
        if stipend1 <= stipend2:
            stipend1, stipend2 = stipend2, stipend1
        
        assume(stipend1 > stipend2)
        
        # Create preferences with min_stipend below both
        min_stipend = min(stipend1, stipend2) - 1000
        preferences = preferences_data.draw(user_preferences_strategy(min_stip=max(0, min_stipend), reject_kw=[]))
        
        # Create two listings with different stipends
        listing1 = JobListing(
            title="Test Title 1",
            company="Test Company",
            stipend=stipend1,
            location="Test Location",
            description="Test description",
            url="http://test.com/1",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text=str(stipend1)
        )
        
        listing2 = JobListing(
            title="Test Title 2",
            company="Test Company",
            stipend=stipend2,
            location="Test Location",
            description="Test description",
            url="http://test.com/2",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text=str(stipend2)
        )
        
        # Score both listings
        engine = ScoringEngine(preferences)
        result1 = engine.score_listing(listing1)
        result2 = engine.score_listing(listing2)
        
        # If either was rejected, skip
        assume(result1 is not None and result2 is not None)
        
        # Stipend score for listing1 should be >= listing2
        assert result1.score_breakdown['stipend'] >= result2.score_breakdown['stipend'], \
            f"Higher stipend (₹{stipend1}) should have >= score than lower stipend (₹{stipend2}), " \
            f"got {result1.score_breakdown['stipend']} vs {result2.score_breakdown['stipend']}"


class TestScoreBasedSorting:
    """
    Property 8: Score-based sorting
    
    For any list of scored listings, the output should be sorted in descending order by score.
    
    Validates: Requirements 4.8
    """
    
    @settings(max_examples=100)
    @given(
        listings=st.lists(job_listing_strategy(), min_size=2, max_size=20),
        preferences_data=st.data()
    )
    def test_score_all_returns_descending_order(self, listings, preferences_data):
        """
        **Feature: internhunt-v6, Property 8: Score-based sorting**
        **Validates: Requirements 4.8**
        
        Test that score_all returns listings in descending score order.
        """
        # Create preferences
        preferences = preferences_data.draw(user_preferences_strategy(reject_kw=[]))
        
        # Score all listings
        engine = ScoringEngine(preferences)
        scored = engine.score_all(listings)
        
        # Need at least 2 scored listings to check ordering
        assume(len(scored) >= 2)
        
        # Check that scores are in descending order
        for i in range(len(scored) - 1):
            assert scored[i].score >= scored[i + 1].score, \
                f"Scores should be in descending order: {scored[i].score} >= {scored[i + 1].score}"
