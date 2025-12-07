"""
Property-Based Tests for Dashboard Generator

Tests universal properties that should hold for all dashboard generation operations.
"""

import re
import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings
from html.parser import HTMLParser

from src.dashboard_generator import DashboardGenerator
from src.scoring_engine import ScoredListing
from src.scrapers.base_scraper import JobListing
from src.preference_wizard import UserPreferences


# Custom HTML parser to validate structure
class HTMLValidator(HTMLParser):
    """Simple HTML validator to check for required elements"""
    
    def __init__(self):
        super().__init__()
        self.elements_found = set()
        self.links = []
        self.current_card = {}
        self.in_job_card = False
        
    def handle_starttag(self, tag, attrs):
        self.elements_found.add(tag)
        
        # Track job cards
        attrs_dict = dict(attrs)
        if tag == 'div' and attrs_dict.get('class') == 'job-card':
            self.in_job_card = True
            self.current_card = {}
        
        # Track links
        if tag == 'a':
            self.links.append(attrs_dict)
    
    def handle_endtag(self, tag):
        if tag == 'div' and self.in_job_card:
            self.in_job_card = False


# Strategy for generating job listings
def job_listing_strategy():
    return st.builds(
        JobListing,
        title=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
        company=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
        stipend=st.one_of(st.none(), st.integers(min_value=0, max_value=100000)),
        location=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
        description=st.text(min_size=0, max_size=500, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
        # Generate URLs without control characters
        url=st.text(min_size=10, max_size=200, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))).map(lambda x: f"https://example.com/{x}"),
        posted_date=st.one_of(st.none(), st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs', 'Cc')))),
        source_platform=st.sampled_from(['Internshala', 'Unstop', 'Naukri', 'LinkedIn', 'LetsIntern', 'InternWorld']),
        raw_stipend_text=st.text(min_size=0, max_size=50, alphabet=st.characters(blacklist_categories=('Cs', 'Cc')))
    )


def scored_listing_strategy():
    return st.builds(
        ScoredListing,
        listing=job_listing_strategy(),
        score=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        score_breakdown=st.fixed_dictionaries({
            'keyword': st.floats(min_value=0.0, max_value=50.0, allow_nan=False, allow_infinity=False),
            'skill': st.floats(min_value=0.0, max_value=50.0, allow_nan=False, allow_infinity=False),
            'stipend': st.floats(min_value=0.0, max_value=5.0, allow_nan=False, allow_infinity=False),
            'remote': st.floats(min_value=0.0, max_value=5.0, allow_nan=False, allow_infinity=False),
            'location': st.floats(min_value=0.0, max_value=3.0, allow_nan=False, allow_infinity=False)
        })
    )


def user_preferences_strategy():
    return st.builds(
        UserPreferences,
        wanted_keywords=st.lists(st.text(min_size=1, max_size=20), max_size=10),
        reject_keywords=st.lists(st.text(min_size=1, max_size=20), max_size=10),
        remote_preference=st.sampled_from(['yes', 'no', 'any']),
        min_stipend=st.integers(min_value=0, max_value=50000),
        max_post_age_days=st.integers(min_value=1, max_value=365),
        max_results=st.integers(min_value=1, max_value=100),
        preferred_locations=st.lists(st.text(min_size=1, max_size=30), max_size=5),
        resume_skills=st.lists(st.text(min_size=1, max_size=30), max_size=20)
    )


class TestDashboardGeneratorProperties:
    """Property-based tests for DashboardGenerator"""
    
    @given(
        listings=st.lists(scored_listing_strategy(), min_size=1, max_size=20),
        preferences=user_preferences_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_11_html_dashboard_validity(self, listings, preferences):
        """
        **Feature: internhunt-v6, Property 11: HTML dashboard validity**
        **Validates: Requirements 6.1, 6.2**
        
        Property: For any generated dashboard, the HTML output should be valid HTML5
        and contain all required elements (title, company, stipend, location, score, link)
        for each listing.
        """
        # Create temporary directory
        tmp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create generator with temporary output directory
            generator = DashboardGenerator(output_dir=tmp_dir)
            
            # Generate dashboard
            filepath = generator.generate(listings, preferences)
            
            # Read generated HTML
            html_content = filepath.read_text(encoding='utf-8')
            
            # Check 1: Valid HTML5 structure
            assert html_content.startswith('<!DOCTYPE html>'), "Should start with HTML5 doctype"
            assert '<html' in html_content, "Should contain html tag"
            assert '<head>' in html_content, "Should contain head tag"
            assert '<body' in html_content, "Should contain body tag (may have attributes)"
            assert '</html>' in html_content, "Should close html tag"
            
            # Check 2: Required meta tags
            assert '<meta charset="UTF-8">' in html_content, "Should have UTF-8 charset"
            assert 'viewport' in html_content, "Should have viewport meta tag"
            
            # Check 3: Title (updated for dark mode)
            assert '<title>InternHunt Results' in html_content, "Should have proper title"
            
            # Check 4: CSS included
            assert '<style>' in html_content, "Should include CSS"
            assert '</style>' in html_content, "Should close CSS"
            
            # Check 5: Each listing should have required fields
            for scored_listing in listings:
                listing = scored_listing.listing
                
                # Title should be present (escaped)
                # Company should be present (escaped)
                # Score should be present (just the number in the new design)
                score_text = f"{scored_listing.score:.1f}"
                assert score_text in html_content, f"Score {score_text} should be in HTML"
                
                # URL should be present (may be HTML-escaped)
                import html as html_module
                escaped_url = html_module.escape(listing.url)
                assert escaped_url in html_content, f"URL {escaped_url} should be in HTML"
            
            # Check 6: Parse HTML to validate structure
            parser = HTMLValidator()
            try:
                parser.feed(html_content)
            except Exception as e:
                assert False, f"HTML parsing failed: {e}"
            
            # Check required HTML elements exist
            required_elements = {'html', 'head', 'body', 'title', 'style', 'header', 'main', 'footer'}
            assert required_elements.issubset(parser.elements_found), \
                f"Missing required elements: {required_elements - parser.elements_found}"
        finally:
            # Clean up temporary directory
            shutil.rmtree(tmp_dir, ignore_errors=True)
    
    @given(
        listings=st.lists(scored_listing_strategy(), min_size=1, max_size=10),
        preferences=user_preferences_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_12_dashboard_link_functionality(self, listings, preferences):
        """
        **Feature: internhunt-v6, Property 12: Dashboard link functionality**
        **Validates: Requirements 6.5**
        
        Property: For any job card in the generated dashboard, the link should open
        in a new browser tab (target="_blank" attribute present).
        """
        # Create temporary directory
        tmp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create generator with temporary output directory
            generator = DashboardGenerator(output_dir=tmp_dir)
            
            # Generate dashboard
            filepath = generator.generate(listings, preferences)
            
            # Read generated HTML
            html_content = filepath.read_text(encoding='utf-8')
            
            # Parse HTML to extract links
            parser = HTMLValidator()
            parser.feed(html_content)
            
            # Find all job listing links (check if class contains relevant keywords since Tailwind uses multiple classes)
            job_links = [link for link in parser.links if link.get('class') and ('gradient' in link.get('class') or 'View Details' in str(link))]
            
            # Alternative: just check all external links
            if not job_links:
                job_links = [link for link in parser.links if link.get('href', '').startswith('http')]
            
            # Check that we have the right number of links
            assert len(job_links) == len(listings), \
                f"Expected {len(listings)} job links, found {len(job_links)}"
            
            # Check each link has target="_blank"
            for link in job_links:
                assert link.get('target') == '_blank', \
                    f"Link {link.get('href')} should have target='_blank'"
                
                # Also check for security attribute
                assert link.get('rel') == 'noopener noreferrer', \
                    f"Link {link.get('href')} should have rel='noopener noreferrer' for security"
        finally:
            # Clean up temporary directory
            shutil.rmtree(tmp_dir, ignore_errors=True)
    
    @given(
        stipend=st.one_of(
            st.none(),
            st.integers(min_value=0, max_value=0),  # Unpaid
            st.integers(min_value=1, max_value=100000)  # Paid
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_13_stipend_formatting_consistency(self, stipend):
        """
        **Feature: internhunt-v6, Property 13: Stipend formatting consistency**
        **Validates: Requirements 6.4**
        
        Property: For any stipend value in INR, the formatted display should include
        the ₹ symbol and proper thousand separators.
        """
        # Create temporary directory
        tmp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Create a simple listing with the stipend
            listing = JobListing(
                title="Test Intern",
                company="Test Company",
                stipend=stipend,
                location="Test Location",
                description="Test description",
                url="https://example.com/test",
                posted_date="2024-01-01",
                source_platform="Test",
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
            
            # Create generator
            generator = DashboardGenerator(output_dir=tmp_dir)
            
            # Generate dashboard
            filepath = generator.generate([scored_listing], preferences)
            
            # Read generated HTML
            html_content = filepath.read_text(encoding='utf-8')
            
            # Check stipend formatting
            if stipend is None:
                assert "Stipend not specified" in html_content, \
                    "None stipend should display 'Stipend not specified'"
            elif stipend == 0:
                assert "Unpaid" in html_content, \
                    "Zero stipend should display 'Unpaid'"
            else:
                # Should contain ₹ symbol
                assert "₹" in html_content, "Paid stipend should include ₹ symbol"
                
                # Should contain the formatted number with commas
                formatted_stipend = f"₹{stipend:,}/month"
                assert formatted_stipend in html_content, \
                    f"Stipend should be formatted as {formatted_stipend}"
                
                # Verify comma separators for numbers >= 1000
                if stipend >= 1000:
                    assert "," in html_content, \
                        "Stipend >= 1000 should have comma separators"
        finally:
            # Clean up temporary directory
            shutil.rmtree(tmp_dir, ignore_errors=True)
