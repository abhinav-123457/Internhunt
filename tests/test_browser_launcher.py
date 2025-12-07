"""
Unit tests for the Browser Launcher module.

Tests cover:
- Successful browser launch
- Failure handling for non-existent files
- Failure handling for browser errors
- Fallback message generation
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.browser_launcher import BrowserLauncher


class TestBrowserLauncher:
    """Test suite for BrowserLauncher class."""
    
    def test_open_dashboard_success(self, tmp_path):
        """
        Test successful browser launch with valid HTML file.
        
        Requirements: 7.1
        """
        # Create a temporary HTML file
        html_file = tmp_path / "test_dashboard.html"
        html_file.write_text("<html><body>Test</body></html>")
        
        # Mock webbrowser.open to return success
        with patch('webbrowser.open', return_value=True) as mock_open:
            result = BrowserLauncher.open_dashboard(html_file)
            
            # Verify browser was called with correct URL
            assert result is True
            mock_open.assert_called_once()
            call_args = mock_open.call_args[0][0]
            assert call_args.startswith("file://")
            assert str(html_file.resolve()) in call_args
    
    def test_open_dashboard_file_not_exists(self, tmp_path):
        """
        Test failure handling when file doesn't exist.
        
        Requirements: 7.2
        """
        # Use a non-existent file path
        non_existent_file = tmp_path / "does_not_exist.html"
        
        result = BrowserLauncher.open_dashboard(non_existent_file)
        
        # Should return False without attempting to open browser
        assert result is False
    
    def test_open_dashboard_browser_failure(self, tmp_path):
        """
        Test failure handling when browser returns failure.
        
        Requirements: 7.2
        """
        # Create a temporary HTML file
        html_file = tmp_path / "test_dashboard.html"
        html_file.write_text("<html><body>Test</body></html>")
        
        # Mock webbrowser.open to return failure
        with patch('webbrowser.open', return_value=False):
            result = BrowserLauncher.open_dashboard(html_file)
            
            # Should return False
            assert result is False
    
    def test_open_dashboard_exception_handling(self, tmp_path):
        """
        Test exception handling during browser launch.
        
        Requirements: 7.2
        """
        # Create a temporary HTML file
        html_file = tmp_path / "test_dashboard.html"
        html_file.write_text("<html><body>Test</body></html>")
        
        # Mock webbrowser.open to raise an exception
        with patch('webbrowser.open', side_effect=Exception("Browser error")):
            result = BrowserLauncher.open_dashboard(html_file)
            
            # Should return False and handle exception gracefully
            assert result is False
    
    def test_get_fallback_message(self, tmp_path):
        """
        Test fallback message generation.
        
        Requirements: 7.2
        """
        # Create a test file path
        html_file = tmp_path / "test_dashboard.html"
        
        message = BrowserLauncher.get_fallback_message(html_file)
        
        # Verify message contains file path and instructions
        assert "Dashboard saved to:" in message
        assert str(html_file.resolve()) in message
        assert "Please open this file manually" in message
    
    def test_open_dashboard_with_relative_path(self, tmp_path):
        """
        Test that relative paths are converted to absolute paths.
        
        Requirements: 7.1
        """
        # Create a temporary HTML file
        html_file = tmp_path / "test_dashboard.html"
        html_file.write_text("<html><body>Test</body></html>")
        
        # Mock webbrowser.open
        with patch('webbrowser.open', return_value=True) as mock_open:
            result = BrowserLauncher.open_dashboard(html_file)
            
            # Verify absolute path was used
            assert result is True
            call_args = mock_open.call_args[0][0]
            # Should contain absolute path
            assert str(html_file.resolve()) in call_args
    
    def test_open_dashboard_logs_success(self, tmp_path, caplog):
        """
        Test that successful browser launch is logged.
        
        Requirements: 7.1
        """
        import logging
        caplog.set_level(logging.INFO)
        
        # Create a temporary HTML file
        html_file = tmp_path / "test_dashboard.html"
        html_file.write_text("<html><body>Test</body></html>")
        
        # Mock webbrowser.open
        with patch('webbrowser.open', return_value=True):
            BrowserLauncher.open_dashboard(html_file)
            
            # Verify success was logged
            assert "Dashboard opened successfully" in caplog.text
    
    def test_open_dashboard_logs_failure(self, tmp_path, caplog):
        """
        Test that browser launch failures are logged.
        
        Requirements: 7.2
        """
        import logging
        caplog.set_level(logging.ERROR)
        
        # Use a non-existent file
        non_existent_file = tmp_path / "does_not_exist.html"
        
        BrowserLauncher.open_dashboard(non_existent_file)
        
        # Verify error was logged
        assert "does not exist" in caplog.text.lower()
