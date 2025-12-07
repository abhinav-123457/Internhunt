"""
Browser Launcher Module

This module provides functionality to automatically open the generated HTML dashboard
in the user's default web browser.
"""

import webbrowser
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class BrowserLauncher:
    """
    Handles opening HTML files in the default system browser.
    
    This class provides a simple interface to launch the generated dashboard
    in the user's default browser, with graceful fallback handling if the
    browser cannot be opened automatically.
    """
    
    @staticmethod
    def open_dashboard(file_path: Path) -> bool:
        """
        Open an HTML file in the default system browser.
        
        Args:
            file_path: Path to the HTML file to open
            
        Returns:
            bool: True if the browser was opened successfully, False otherwise
            
        Requirements:
            - 7.1: Automatically open the file in the default system browser
            - 7.2: Handle failures gracefully with fallback message
        """
        try:
            # Validate that the file exists
            if not file_path.exists():
                logger.error(f"Dashboard file does not exist: {file_path}")
                return False
            
            # Convert to absolute path and create file:// URL
            absolute_path = file_path.resolve()
            file_url = f"file://{absolute_path}"
            
            # Attempt to open in default browser
            logger.info(f"Opening dashboard in browser: {file_url}")
            success = webbrowser.open(file_url)
            
            if success:
                logger.info("Dashboard opened successfully in browser")
                return True
            else:
                logger.warning("Browser returned failure status")
                return False
                
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
            return False
    
    @staticmethod
    def get_fallback_message(file_path: Path) -> str:
        """
        Generate a fallback message for manual opening.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            str: User-friendly message with file path for manual opening
        """
        absolute_path = file_path.resolve()
        return (
            f"Dashboard saved to: {absolute_path}\n"
            f"Please open this file manually in your browser."
        )
