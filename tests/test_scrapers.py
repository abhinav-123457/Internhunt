"""
Unit tests for platform-specific scrapers.

Tests parsing of all required fields and handling of missing fields
using mock HTML responses for each platform.
"""

import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass

from src.scrapers.internshala_scraper import InternshalaScr
from src.scrapers.unstop_scraper import UnstopScraper
from src.scrapers.naukri_scraper import NaukriScraper
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.scrapers.letsintern_scraper import LetsInternScraper
from src.scrapers.internworld_scraper import InternWorldScraper
from src.scrapers.base_scraper import JobListing


@dataclass
class MockPreferences:
    """Mock UserPreferences for testing"""
    wanted_keywords: list
    reject_keywords: list
    remote_preference: str
    min_stipend: int
    max_post_age_days: int
    max_results: int
    preferred_locations: list
    resume_skills: list


# Mock HTML responses for each platform
INTERNSHALA_HTML = """
<html>
<body>
    <div class="internship_meta">
        <h3 class="heading_4_5">Python Developer Intern</h3>
        <p class="company_name">TechCorp India</p>
        <p class="location_link">Bangalore</p>
        <span class="stipend">₹15,000/month</span>
        <div class="internship_other_details_container">
            Work on Python projects and Django framework
        </div>
        <a class="view_detail_button" href="/internship/detail/python-developer-123">View Details</a>
        <div class="status">Posted 2 days ago</div>
    </div>
</body>
</html>
"""

INTERNSHALA_HTML_MISSING_FIELDS = """
<html>
<body>
    <div class="internship_meta">
        <h3 class="heading_4_5">ML Intern</h3>
        <p class="company_name">AI Startup</p>
    </div>
</body>
</html>
"""

UNSTOP_HTML = """
<html>
<body>
    <div class="opportunity-card">
        <h3>Data Science Intern</h3>
        <div class="company">DataCo</div>
        <div class="location">Remote</div>
        <div class="stipend">₹20,000</div>
        <div class="description">Work on ML models</div>
        <a href="/opportunity/data-science-456">Apply</a>
        <div class="date">3 days ago</div>
    </div>
</body>
</html>
"""

NAUKRI_HTML = """
<html>
<body>
    <article class="jobTuple">
        <a class="title">Software Intern</a>
        <a class="comp-name">SoftwareCo</a>
        <span class="loc">Mumbai</span>
        <span class="sal">₹10,000-₹15,000</span>
        <div class="job-description">Develop web applications</div>
        <span class="date">1 week ago</span>
    </article>
</body>
</html>
"""

LINKEDIN_HTML = """
<html>
<body>
    <div class="job-search-card">
        <h3 class="base-search-card__title">Marketing Intern</h3>
        <h4 class="base-search-card__subtitle">MarketingCorp</h4>
        <span class="job-search-card__location">Delhi</span>
        <p class="job-search-card__snippet">Digital marketing role</p>
        <a class="base-card__full-link" href="/jobs/view/789">View</a>
        <time class="job-search-card__listdate" datetime="2024-01-15">2024-01-15</time>
    </div>
</body>
</html>
"""

LETSINTERN_HTML = """
<html>
<body>
    <div class="internship-card">
        <h3 class="title">Content Writer Intern</h3>
        <div class="company">ContentCo</div>
        <div class="location">Pune</div>
        <div class="stipend">₹8,000</div>
        <div class="description">Write blog posts</div>
        <a class="apply-link" href="/internships/content-writer-101">Apply</a>
        <div class="posted-date">5 days ago</div>
    </div>
</body>
</html>
"""

INTERNWORLD_HTML = """
<html>
<body>
    <div class="listing">
        <h3 class="job-title">Design Intern</h3>
        <div class="company-name">DesignStudio</div>
        <div class="job-location">Hyderabad</div>
        <div class="stipend">₹12,000</div>
        <div class="job-description">UI/UX design work</div>
        <a class="view-details" href="/internships/design-202">Details</a>
        <div class="posted-on">1 day ago</div>
    </div>
</body>
</html>
"""


class TestInternshalaScr:
    """Tests for Internshala scraper"""
    
    def test_parse_complete_listing(self):
        """Test parsing a complete listing with all fields"""
        scraper = InternshalaScr()
        
        with patch.object(scraper, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.text = INTERNSHALA_HTML
            mock_request.return_value = mock_response
            
            preferences = MockPreferences(
                wanted_keywords=['python'],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            listings = scraper.scrape(preferences)
            
            assert len(listings) == 1
            listing = listings[0]
            assert listing.title == "Python Developer Intern"
            assert listing.company == "TechCorp India"
            assert listing.location == "Bangalore"
            assert listing.stipend == 15000
            assert "Python projects" in listing.description
            assert listing.source_platform == "Internshala"
            assert listing.posted_date == "Posted 2 days ago"
    
    def test_parse_missing_fields(self):
        """Test handling of missing fields"""
        scraper = InternshalaScr()
        
        with patch.object(scraper, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.text = INTERNSHALA_HTML_MISSING_FIELDS
            mock_request.return_value = mock_response
            
            preferences = MockPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            listings = scraper.scrape(preferences)
            
            assert len(listings) == 1
            listing = listings[0]
            assert listing.title == "ML Intern"
            assert listing.company == "AI Startup"
            assert listing.location == "Not specified"
            assert listing.stipend is None
            assert listing.posted_date is None


class TestUnstopScraper:
    """Tests for Unstop scraper"""
    
    def test_parse_complete_listing(self):
        """Test parsing a complete listing with all fields"""
        scraper = UnstopScraper()
        
        with patch.object(scraper, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.text = UNSTOP_HTML
            mock_request.return_value = mock_response
            
            preferences = MockPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            listings = scraper.scrape(preferences)
            
            assert len(listings) == 1
            listing = listings[0]
            assert listing.title == "Data Science Intern"
            assert listing.company == "DataCo"
            assert listing.location == "Remote"
            assert listing.stipend == 20000
            assert listing.source_platform == "Unstop"


class TestNaukriScraper:
    """Tests for Naukri scraper"""
    
    def test_parse_complete_listing(self):
        """Test parsing a complete listing with all fields"""
        scraper = NaukriScraper()
        
        with patch.object(scraper, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.text = NAUKRI_HTML
            mock_request.return_value = mock_response
            
            preferences = MockPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            listings = scraper.scrape(preferences)
            
            assert len(listings) == 1
            listing = listings[0]
            assert listing.title == "Software Intern"
            assert listing.company == "SoftwareCo"
            assert listing.location == "Mumbai"
            assert listing.stipend == 10000  # Should take minimum from range
            assert listing.source_platform == "Naukri"


class TestLinkedInScraper:
    """Tests for LinkedIn scraper"""
    
    def test_parse_complete_listing(self):
        """Test parsing a complete listing with all fields"""
        scraper = LinkedInScraper()
        
        with patch.object(scraper, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.text = LINKEDIN_HTML
            mock_request.return_value = mock_response
            
            preferences = MockPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            listings = scraper.scrape(preferences)
            
            assert len(listings) == 1
            listing = listings[0]
            assert listing.title == "Marketing Intern"
            assert listing.company == "MarketingCorp"
            assert listing.location == "Delhi"
            assert listing.source_platform == "LinkedIn"
            assert listing.posted_date == "2024-01-15"


class TestLetsInternScraper:
    """Tests for LetsIntern scraper"""
    
    def test_parse_complete_listing(self):
        """Test parsing a complete listing with all fields"""
        scraper = LetsInternScraper()
        
        with patch.object(scraper, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.text = LETSINTERN_HTML
            mock_request.return_value = mock_response
            
            preferences = MockPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            listings = scraper.scrape(preferences)
            
            assert len(listings) == 1
            listing = listings[0]
            assert listing.title == "Content Writer Intern"
            assert listing.company == "ContentCo"
            assert listing.location == "Pune"
            assert listing.stipend == 8000
            assert listing.source_platform == "LetsIntern"


class TestInternWorldScraper:
    """Tests for InternWorld scraper"""
    
    def test_parse_complete_listing(self):
        """Test parsing a complete listing with all fields"""
        scraper = InternWorldScraper()
        
        with patch.object(scraper, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.text = INTERNWORLD_HTML
            mock_request.return_value = mock_response
            
            preferences = MockPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            listings = scraper.scrape(preferences)
            
            assert len(listings) == 1
            listing = listings[0]
            assert listing.title == "Design Intern"
            assert listing.company == "DesignStudio"
            assert listing.location == "Hyderabad"
            assert listing.stipend == 12000
            assert listing.source_platform == "InternWorld"


class TestScraperErrorHandling:
    """Tests for error handling across all scrapers"""
    
    def test_network_failure_returns_empty_list(self):
        """Test that network failures return empty list instead of crashing"""
        scraper = InternshalaScr()
        
        with patch.object(scraper, '_make_request') as mock_request:
            mock_request.return_value = None  # Simulate network failure
            
            preferences = MockPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            listings = scraper.scrape(preferences)
            
            assert listings == []
    
    def test_invalid_html_returns_empty_list(self):
        """Test that invalid HTML returns empty list"""
        scraper = UnstopScraper()
        
        with patch.object(scraper, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.text = "<html><body>No cards here</body></html>"
            mock_request.return_value = mock_response
            
            preferences = MockPreferences(
                wanted_keywords=[],
                reject_keywords=[],
                remote_preference='any',
                min_stipend=0,
                max_post_age_days=30,
                max_results=50,
                preferred_locations=[],
                resume_skills=[]
            )
            
            listings = scraper.scrape(preferences)
            
            assert listings == []
