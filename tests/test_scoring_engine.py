"""
Unit Tests for Scoring Engine

Tests specific scoring components and edge cases.
"""

import pytest

from src.scoring_engine import ScoringEngine, ScoredListing
from src.scrapers.base_scraper import JobListing
from src.preference_wizard import UserPreferences


class TestKeywordMatching:
    """Test keyword matching functionality"""
    
    def test_keyword_match_in_title(self):
        """Test that keywords in title are matched"""
        preferences = UserPreferences(
            wanted_keywords=['python', 'machine learning'],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        listing = JobListing(
            title="Python Developer Intern",
            company="Tech Corp",
            stipend=15000,
            location="Bangalore",
            description="Looking for interns",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        assert result is not None
        # Should match 'python' (10 points - increased from 2)
        assert result.score_breakdown['keyword'] == 10.0
    
    def test_keyword_match_in_description(self):
        """Test that keywords in description are matched"""
        preferences = UserPreferences(
            wanted_keywords=['python', 'machine learning'],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        listing = JobListing(
            title="Developer Intern",
            company="Tech Corp",
            stipend=15000,
            location="Bangalore",
            description="We need someone with Python and Machine Learning experience",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        assert result is not None
        # Should match both 'python' and 'machine learning' (20 points - increased from 4)
        assert result.score_breakdown['keyword'] == 20.0
    
    def test_keyword_case_insensitive(self):
        """Test that keyword matching is case-insensitive"""
        preferences = UserPreferences(
            wanted_keywords=['python'],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        listing = JobListing(
            title="PYTHON Developer",
            company="Tech Corp",
            stipend=15000,
            location="Bangalore",
            description="Python programming",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        assert result is not None
        # Should match 'python' in both title and description (but count once per occurrence)
        assert result.score_breakdown['keyword'] == 10.0  # Increased from 2.0
    
    def test_no_keyword_matches(self):
        """Test listing with no keyword matches - should be rejected"""
        preferences = UserPreferences(
            wanted_keywords=['java', 'spring'],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        listing = JobListing(
            title="Python Developer",
            company="Tech Corp",
            stipend=15000,
            location="Bangalore",
            description="Python and Django",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        # Listings with zero keyword matches are rejected when keywords are specified
        assert result is None


class TestSkillMatching:
    """Test skill matching functionality"""
    
    def test_skill_match_in_description(self):
        """Test that resume skills are matched in description"""
        preferences = UserPreferences(
            wanted_keywords=[],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=['python', 'tensorflow', 'docker']
        )
        
        listing = JobListing(
            title="ML Intern",
            company="AI Corp",
            stipend=20000,
            location="Remote",
            description="Looking for someone with Python, TensorFlow, and Docker experience",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="20000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        assert result is not None
        # Should match all 3 skills (9 points - increased from 3)
        assert result.score_breakdown['skill'] == 9.0
    
    def test_skill_word_boundary_matching(self):
        """Test that skill matching uses word boundaries"""
        preferences = UserPreferences(
            wanted_keywords=[],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=['go']
        )
        
        listing = JobListing(
            title="Backend Developer",
            company="Tech Corp",
            stipend=15000,
            location="Bangalore",
            description="We need Go programming skills",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        assert result is not None
        # Should match 'go' as a word (3 points - increased from 1)
        assert result.score_breakdown['skill'] == 3.0
    
    def test_no_skill_matches(self):
        """Test listing with no skill matches"""
        preferences = UserPreferences(
            wanted_keywords=[],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=['java', 'spring']
        )
        
        listing = JobListing(
            title="Python Developer",
            company="Tech Corp",
            stipend=15000,
            location="Bangalore",
            description="Python and Django",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        assert result is not None
        assert result.score_breakdown['skill'] == 0.0


class TestLocationMatching:
    """Test location matching functionality"""
    
    def test_location_match(self):
        """Test that preferred locations are matched"""
        preferences = UserPreferences(
            wanted_keywords=[],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=['bangalore', 'mumbai'],
            resume_skills=[]
        )
        
        listing = JobListing(
            title="Developer Intern",
            company="Tech Corp",
            stipend=15000,
            location="Bangalore, Karnataka",
            description="Office based role",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        assert result is not None
        # Should match 'bangalore' (5 points - increased from 3)
        assert result.score_breakdown['location'] == 5.0
    
    def test_location_case_insensitive(self):
        """Test that location matching is case-insensitive"""
        preferences = UserPreferences(
            wanted_keywords=[],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=['bangalore'],
            resume_skills=[]
        )
        
        listing = JobListing(
            title="Developer Intern",
            company="Tech Corp",
            stipend=15000,
            location="BANGALORE",
            description="Office based role",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        assert result is not None
        assert result.score_breakdown['location'] == 5.0  # Increased from 3.0
    
    def test_no_location_match(self):
        """Test listing with no location match"""
        preferences = UserPreferences(
            wanted_keywords=[],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=['delhi', 'pune'],
            resume_skills=[]
        )
        
        listing = JobListing(
            title="Developer Intern",
            company="Tech Corp",
            stipend=15000,
            location="Bangalore",
            description="Office based role",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        assert result is not None
        assert result.score_breakdown['location'] == 0.0


class TestScoreCalculation:
    """Test overall score calculation"""
    
    def test_total_score_is_sum_of_components(self):
        """Test that total score equals sum of all components"""
        preferences = UserPreferences(
            wanted_keywords=['python'],
            reject_keywords=[],
            remote_preference='yes',
            min_stipend=10000,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=['bangalore'],
            resume_skills=['django']
        )
        
        listing = JobListing(
            title="Python Developer",
            company="Tech Corp",
            stipend=25000,
            location="Bangalore, Remote",
            description="Django and Python experience required",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="25000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        assert result is not None
        
        # Calculate expected total
        expected_total = (
            result.score_breakdown['keyword'] +
            result.score_breakdown['skill'] +
            result.score_breakdown['stipend'] +
            result.score_breakdown['remote'] +
            result.score_breakdown['location']
        )
        
        assert result.score == expected_total
    
    def test_stipend_below_minimum_not_rejected(self):
        """Test that listings with stipend below minimum are NOT rejected (shown with lower score)"""
        preferences = UserPreferences(
            wanted_keywords=['python'],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=20000,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        listing = JobListing(
            title="Python Developer",
            company="Tech Corp",
            stipend=15000,  # Below minimum
            location="Bangalore",
            description="Python programming",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        # NEW: Should NOT be rejected, just shown with lower stipend score
        assert result is not None
        assert result.score_breakdown['stipend'] == 0.0  # No bonus for low stipend
    
    def test_none_stipend_not_rejected_by_minimum(self):
        """Test that listings with None stipend are not rejected by minimum stipend"""
        preferences = UserPreferences(
            wanted_keywords=['python'],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=20000,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        listing = JobListing(
            title="Python Developer",
            company="Tech Corp",
            stipend=None,  # Unpaid/not specified
            location="Bangalore",
            description="Python programming",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="Not disclosed"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        # Should not be rejected (None stipend doesn't trigger minimum check)
        assert result is not None
        assert result.score_breakdown['stipend'] == 0.0
    
    def test_stipend_scoring_capped_at_five(self):
        """Test that stipend score is capped at 5 points"""
        preferences = UserPreferences(
            wanted_keywords=[],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=10000,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        listing = JobListing(
            title="Developer",
            company="Tech Corp",
            stipend=100000,  # Very high stipend
            location="Bangalore",
            description="High paying role",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="100000"
        )
        
        engine = ScoringEngine(preferences)
        result = engine.score_listing(listing)
        
        assert result is not None
        # Stipend score should be capped at 3.0 (reduced from 5.0)
        assert result.score_breakdown['stipend'] == 3.0
    
    def test_remote_score_only_when_user_wants_remote(self):
        """Test that remote score is only given when user wants remote"""
        # User wants remote
        preferences_yes = UserPreferences(
            wanted_keywords=[],
            reject_keywords=[],
            remote_preference='yes',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        # User doesn't want remote
        preferences_no = UserPreferences(
            wanted_keywords=[],
            reject_keywords=[],
            remote_preference='no',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        listing = JobListing(
            title="Developer",
            company="Tech Corp",
            stipend=15000,
            location="Remote",
            description="Work from home",
            url="http://test.com",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        engine_yes = ScoringEngine(preferences_yes)
        result_yes = engine_yes.score_listing(listing)
        
        engine_no = ScoringEngine(preferences_no)
        result_no = engine_no.score_listing(listing)
        
        assert result_yes is not None
        assert result_no is not None
        
        # Should get remote score when user wants remote
        assert result_yes.score_breakdown['remote'] == 5.0
        # Should not get remote score when user doesn't want remote
        assert result_no.score_breakdown['remote'] == 0.0


class TestScoreAllSorting:
    """Test score_all sorting functionality"""
    
    def test_score_all_sorts_by_score(self):
        """Test that score_all returns listings sorted by score"""
        preferences = UserPreferences(
            wanted_keywords=['python'],
            reject_keywords=[],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        # Create listings with different scores
        listing1 = JobListing(
            title="Java Developer",  # No keyword match - will be REJECTED
            company="Tech Corp",
            stipend=15000,
            location="Bangalore",
            description="Java programming",
            url="http://test.com/1",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        listing2 = JobListing(
            title="Python Developer",  # Keyword match (10 points)
            company="Tech Corp",
            stipend=15000,
            location="Bangalore",
            description="Python programming",
            url="http://test.com/2",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        listing3 = JobListing(
            title="Python Expert",  # Keyword match (10 points)
            company="Tech Corp",
            stipend=25000,  # Higher stipend (extra points)
            location="Bangalore",
            description="Python programming",
            url="http://test.com/3",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="25000"
        )
        
        engine = ScoringEngine(preferences)
        scored = engine.score_all([listing1, listing2, listing3])
        
        # Should be sorted by score (highest first)
        # listing1 is rejected due to zero keyword matches
        assert len(scored) == 2
        assert scored[0].listing.url == "http://test.com/3"  # Highest score
        assert scored[1].listing.url == "http://test.com/2"
    
    def test_score_all_excludes_rejected(self):
        """Test that score_all excludes rejected listings"""
        preferences = UserPreferences(
            wanted_keywords=['python'],
            reject_keywords=['unpaid'],
            remote_preference='any',
            min_stipend=0,
            max_post_age_days=30,
            max_results=50,
            preferred_locations=[],
            resume_skills=[]
        )
        
        listing1 = JobListing(
            title="Python Developer",
            company="Tech Corp",
            stipend=15000,
            location="Bangalore",
            description="Python programming",
            url="http://test.com/1",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="15000"
        )
        
        listing2 = JobListing(
            title="Python Intern",
            company="Startup",
            stipend=0,
            location="Remote",
            description="Unpaid internship for Python",  # Contains reject keyword
            url="http://test.com/2",
            posted_date="2024-01-01",
            source_platform="Test",
            raw_stipend_text="Unpaid"
        )
        
        engine = ScoringEngine(preferences)
        scored = engine.score_all([listing1, listing2])
        
        # Should only include listing1
        assert len(scored) == 1
        assert scored[0].listing.url == "http://test.com/1"
