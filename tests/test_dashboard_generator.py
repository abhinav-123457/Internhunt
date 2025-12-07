"""
Unit Tests for Dashboard Generator

Tests specific functionality and edge cases for the dashboard generator.
"""

import tempfile
import shutil
from pathlib import Path

from src.dashboard_generator import DashboardGenerator
from src.scoring_engine import ScoredListing
from src.scrapers.base_scraper import JobListing
from src.preference_wizard import UserPreferences


class TestDashboardGenerator:
    """Unit tests for DashboardGenerator"""
    
    def test_html_structure(self):
        """Test that generated HTML has proper structure"""
        # Create temporary directory
        tmp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create a simple listing
            listing = JobListing(
                title="Software Intern",
                company="Tech Corp",
                stipend=15000,
                location="Bangalore",
                description="Great opportunity",
                url="https://example.com/job1",
                posted_date="2024-01-01",
                source_platform="Internshala",
                raw_stipend_text="₹15,000/month"
            )
            
            scored_listing = ScoredListing(
                listing=listing,
                score=12.5,
                score_breakdown={'keyword': 4.0, 'skill': 3.0, 'stipend': 2.5, 'remote': 0.0, 'location': 3.0}
            )
            
            preferences = UserPreferences(
                wanted_keywords=['software', 'python'],
                reject_keywords=['sales'],
                remote_preference='any',
                min_stipend=10000,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=['bangalore'],
                resume_skills=['python', 'java']
            )
            
            # Generate dashboard
            generator = DashboardGenerator(output_dir=tmp_dir)
            filepath = generator.generate([scored_listing], preferences)
            
            # Read HTML
            html_content = filepath.read_text(encoding='utf-8')
            
            # Check structure
            assert '<!DOCTYPE html>' in html_content
            assert '<html lang="en"' in html_content  # Updated to allow for class attribute
            assert '<head>' in html_content
            assert '<body' in html_content  # Updated to allow for class attribute
            assert '</html>' in html_content
            
            # Check title (updated for dark mode)
            assert '<title>InternHunt Results' in html_content
            
            # Check job card elements
            assert 'Software Intern' in html_content
            assert 'Tech Corp' in html_content
            assert '₹15,000/month' in html_content
            assert 'Bangalore' in html_content
            # Score badge removed - no longer displayed
            assert 'https://example.com/job1' in html_content
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    
    def test_special_character_escaping(self):
        """Test that special HTML characters are properly escaped"""
        tmp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create listing with special characters
            listing = JobListing(
                title="<Script>Alert('XSS')</Script>",
                company="Company & Co.",
                stipend=20000,
                location="City > Town",
                description="Description with \"quotes\" and <tags>",
                url="https://example.com/job?id=1&type=intern",
                posted_date="2024-01-01",
                source_platform="Internshala",
                raw_stipend_text=""
            )
            
            scored_listing = ScoredListing(
                listing=listing,
                score=10.0,
                score_breakdown={'keyword': 10.0, 'skill': 0.0, 'stipend': 0.0, 'remote': 0.0, 'location': 0.0}
            )
            
            preferences = UserPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            # Generate dashboard
            generator = DashboardGenerator(output_dir=tmp_dir)
            filepath = generator.generate([scored_listing], preferences)
            
            # Read HTML
            html_content = filepath.read_text(encoding='utf-8')
            
            # Check that special characters are escaped
            assert '&lt;Script&gt;' in html_content  # < and > escaped
            assert '&amp;' in html_content  # & escaped
            assert '<Script>' not in html_content  # Raw script tag should not be present
            
            # Check URL is properly escaped
            assert '&amp;' in html_content  # & in URL should be escaped
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    
    def test_empty_results_handling(self):
        """Test dashboard generation with no results"""
        tmp_dir = Path(tempfile.mkdtemp())
        
        try:
            preferences = UserPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            # Generate dashboard with empty list
            generator = DashboardGenerator(output_dir=tmp_dir)
            filepath = generator.generate([], preferences)
            
            # Read HTML
            html_content = filepath.read_text(encoding='utf-8')
            
            # Check for no results message (updated text)
            assert 'No internships found' in html_content
            
            # Should still have valid HTML structure
            assert '<!DOCTYPE html>' in html_content
            assert '<html' in html_content
            assert '</html>' in html_content
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    
    def test_css_inclusion(self):
        """Test that CSS is properly included in the HTML"""
        tmp_dir = Path(tempfile.mkdtemp())
        
        try:
            listing = JobListing(
                title="Test Intern",
                company="Test Company",
                stipend=10000,
                location="Test City",
                description="Test description",
                url="https://example.com/test",
                posted_date="2024-01-01",
                source_platform="Internshala",
                raw_stipend_text=""
            )
            
            scored_listing = ScoredListing(
                listing=listing,
                score=5.0,
                score_breakdown={'keyword': 5.0, 'skill': 0.0, 'stipend': 0.0, 'remote': 0.0, 'location': 0.0}
            )
            
            preferences = UserPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            # Generate dashboard
            generator = DashboardGenerator(output_dir=tmp_dir)
            filepath = generator.generate([scored_listing], preferences)
            
            # Read HTML
            html_content = filepath.read_text(encoding='utf-8')
            
            # Check CSS is included
            assert '<style>' in html_content
            assert '</style>' in html_content
            
            # Check for Tailwind CSS CDN
            assert 'tailwindcss.com' in html_content
            
            # Check for key Tailwind classes (not CSS selectors)
            assert 'bg-card' in html_content
            assert 'score-badge' in html_content  # Custom class still used
            
            # Check for responsive design (Tailwind uses responsive prefixes)
            assert 'md:' in html_content or 'lg:' in html_content
            # Tailwind uses utility classes instead of raw CSS
            assert 'grid' in html_content
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    
    def test_timestamped_filename(self):
        """Test that generated files have timestamped names"""
        tmp_dir = Path(tempfile.mkdtemp())
        
        try:
            listing = JobListing(
                title="Test",
                company="Test",
                stipend=None,
                location="Test",
                description="Test",
                url="https://example.com/test",
                posted_date=None,
                source_platform="Internshala",
                raw_stipend_text=""
            )
            
            scored_listing = ScoredListing(
                listing=listing,
                score=0.0,
                score_breakdown={'keyword': 0.0, 'skill': 0.0, 'stipend': 0.0, 'remote': 0.0, 'location': 0.0}
            )
            
            preferences = UserPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            # Generate dashboard
            generator = DashboardGenerator(output_dir=tmp_dir)
            filepath = generator.generate([scored_listing], preferences)
            
            # Check filename format
            assert filepath.name.startswith('internhunt_results_')
            assert filepath.name.endswith('.html')
            assert filepath.parent == tmp_dir
            
            # Check file exists
            assert filepath.exists()
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    
    def test_stipend_formatting_variations(self):
        """Test various stipend formatting scenarios"""
        tmp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Test None stipend
            listing1 = JobListing(
                title="Unpaid Intern",
                company="Startup",
                stipend=None,
                location="Remote",
                description="Test",
                url="https://example.com/1",
                posted_date=None,
                source_platform="Internshala",
                raw_stipend_text=""
            )
            
            # Test zero stipend
            listing2 = JobListing(
                title="Volunteer",
                company="NGO",
                stipend=0,
                location="Delhi",
                description="Test",
                url="https://example.com/2",
                posted_date=None,
                source_platform="Internshala",
                raw_stipend_text=""
            )
            
            # Test paid stipend
            listing3 = JobListing(
                title="Paid Intern",
                company="Corp",
                stipend=25000,
                location="Mumbai",
                description="Test",
                url="https://example.com/3",
                posted_date=None,
                source_platform="Internshala",
                raw_stipend_text=""
            )
            
            scored_listings = [
                ScoredListing(listing1, 1.0, {}),
                ScoredListing(listing2, 2.0, {}),
                ScoredListing(listing3, 3.0, {})
            ]
            
            preferences = UserPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            # Generate dashboard
            generator = DashboardGenerator(output_dir=tmp_dir)
            filepath = generator.generate(scored_listings, preferences)
            
            # Read HTML
            html_content = filepath.read_text(encoding='utf-8')
            
            # Check stipend formatting
            assert 'Stipend not specified' in html_content
            assert 'Unpaid' in html_content
            assert '₹25,000/month' in html_content
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
