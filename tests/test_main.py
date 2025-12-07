"""
Unit tests for main application orchestrator.

Tests the InternHuntApp class and its pipeline orchestration.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from src.main import InternHuntApp
from src.preference_wizard import UserPreferences
from src.scrapers.base_scraper import JobListing
from src.scoring_engine import ScoredListing


class TestInternHuntApp:
    """Test suite for InternHuntApp class"""
    
    def test_initialization(self):
        """Test that InternHuntApp initializes correctly"""
        app = InternHuntApp()
        
        assert app.resume_parser is None  # Lazy loaded
        assert app.preference_wizard is not None
        assert app.scraper_engine is None  # Lazy loaded
        assert app.dashboard_generator is not None
    
    def test_print_welcome(self, capsys):
        """Test welcome message printing"""
        app = InternHuntApp()
        app._print_welcome()
        
        captured = capsys.readouterr()
        assert "InternHunt v6" in captured.out
        assert "Automated Internship Discovery" in captured.out
    
    def test_run_resume_parser_no_resume(self):
        """Test resume parser with no resume provided"""
        app = InternHuntApp()
        skills = app._run_resume_parser(None)
        
        assert skills == []
        assert app.resume_parser is None  # Should not be initialized
    
    @patch('src.main.ResumeParser')
    def test_run_resume_parser_with_resume(self, mock_parser_class, tmp_path):
        """Test resume parser with valid resume"""
        # Create a mock resume file
        resume_path = tmp_path / "resume.pdf"
        resume_path.write_text("dummy content")
        
        # Mock the parser
        mock_parser = Mock()
        mock_result = Mock()
        mock_result.extracted_skills = ["Python", "Machine Learning", "Data Science"]
        mock_parser.parse_resume.return_value = mock_result
        mock_parser_class.return_value = mock_parser
        
        app = InternHuntApp()
        skills = app._run_resume_parser(resume_path)
        
        assert skills == ["Python", "Machine Learning", "Data Science"]
        mock_parser.parse_resume.assert_called_once_with(resume_path)
    
    @patch('src.main.ResumeParser')
    def test_run_resume_parser_failure(self, mock_parser_class, tmp_path):
        """Test resume parser handles failures gracefully"""
        resume_path = tmp_path / "resume.pdf"
        resume_path.write_text("dummy content")
        
        # Mock parser to return None (failure)
        mock_parser = Mock()
        mock_parser.parse_resume.return_value = None
        mock_parser_class.return_value = mock_parser
        
        app = InternHuntApp()
        skills = app._run_resume_parser(resume_path)
        
        assert skills == []
    
    def test_apply_max_results_limit_under_limit(self):
        """Test max results limit when under the limit"""
        app = InternHuntApp()
        
        # Create mock listings
        listings = [
            Mock(score=10.0),
            Mock(score=8.0),
            Mock(score=6.0)
        ]
        
        result = app._apply_max_results_limit(listings, max_results=5)
        
        assert len(result) == 3
        assert result == listings
    
    def test_apply_max_results_limit_over_limit(self):
        """Test max results limit when over the limit"""
        app = InternHuntApp()
        
        # Create mock listings
        listings = [
            Mock(score=10.0),
            Mock(score=8.0),
            Mock(score=6.0),
            Mock(score=4.0),
            Mock(score=2.0)
        ]
        
        result = app._apply_max_results_limit(listings, max_results=3)
        
        assert len(result) == 3
        assert result == listings[:3]
    
    def test_print_summary(self, capsys):
        """Test execution summary printing"""
        app = InternHuntApp()
        dashboard_path = Path("output/test_dashboard.html")
        
        app._print_summary(100, 50, 30, dashboard_path)
        
        captured = capsys.readouterr()
        assert "Execution Summary" in captured.out
        assert "100" in captured.out  # Total scraped
        assert "50" in captured.out   # After filtering
        assert "30" in captured.out   # Final count
        assert "test_dashboard.html" in captured.out
    
    @patch('src.main.ScraperEngine')
    def test_run_scraping(self, mock_scraper_class):
        """Test scraping orchestration"""
        # Mock scraper engine
        mock_engine = Mock()
        mock_listings = [
            Mock(title="Intern 1"),
            Mock(title="Intern 2")
        ]
        mock_engine.scrape_all.return_value = mock_listings
        mock_scraper_class.return_value = mock_engine
        
        app = InternHuntApp()
        preferences = Mock()
        
        result = app._run_scraping(preferences)
        
        assert len(result) == 2
        mock_engine.scrape_all.assert_called_once_with(preferences)
    
    @patch('src.main.ScoringEngine')
    def test_run_scoring(self, mock_scoring_class):
        """Test scoring orchestration"""
        # Mock scoring engine
        mock_engine = Mock()
        mock_scored = [
            Mock(score=10.0),
            Mock(score=8.0)
        ]
        mock_engine.score_all.return_value = mock_scored
        mock_scoring_class.return_value = mock_engine
        
        app = InternHuntApp()
        listings = [Mock(), Mock()]
        preferences = Mock()
        
        result = app._run_scoring(listings, preferences)
        
        assert len(result) == 2
        mock_engine.score_all.assert_called_once_with(listings)
    
    @patch('src.main.Deduplicator')
    def test_run_deduplication(self, mock_dedup_class):
        """Test deduplication orchestration"""
        # Mock deduplicator
        mock_unique = [Mock(score=10.0)]
        mock_dedup_class.deduplicate.return_value = mock_unique
        
        app = InternHuntApp()
        listings = [Mock(), Mock()]
        
        result = app._run_deduplication(listings)
        
        assert len(result) == 1
        mock_dedup_class.deduplicate.assert_called_once_with(listings)
    
    @patch('src.main.DashboardGenerator')
    def test_run_dashboard_generation(self, mock_dashboard_class):
        """Test dashboard generation orchestration"""
        # Mock dashboard generator
        mock_gen = Mock()
        mock_path = Path("output/dashboard.html")
        mock_gen.generate.return_value = mock_path
        mock_dashboard_class.return_value = mock_gen
        
        app = InternHuntApp()
        app.dashboard_generator = mock_gen
        
        listings = [Mock()]
        preferences = Mock()
        
        result = app._run_dashboard_generation(listings, preferences)
        
        assert result == mock_path
        mock_gen.generate.assert_called_once_with(listings, preferences)
    
    @patch('src.main.BrowserLauncher')
    def test_run_browser_launch_success(self, mock_browser_class):
        """Test browser launch with success"""
        mock_browser_class.open_dashboard.return_value = True
        
        app = InternHuntApp()
        dashboard_path = Path("output/dashboard.html")
        
        # Should not raise exception
        app._run_browser_launch(dashboard_path)
        
        mock_browser_class.open_dashboard.assert_called_once_with(dashboard_path)
    
    @patch('src.main.BrowserLauncher')
    def test_run_browser_launch_failure(self, mock_browser_class):
        """Test browser launch with failure"""
        mock_browser_class.open_dashboard.return_value = False
        mock_browser_class.get_fallback_message.return_value = "Fallback message"
        
        app = InternHuntApp()
        dashboard_path = Path("output/dashboard.html")
        
        # Should not raise exception
        app._run_browser_launch(dashboard_path)
        
        mock_browser_class.open_dashboard.assert_called_once_with(dashboard_path)
        mock_browser_class.get_fallback_message.assert_called_once_with(dashboard_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
