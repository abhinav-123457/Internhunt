#!/usr/bin/env python3
"""
InternHunt v6 - Automated Internship Discovery CLI

A Python CLI application that automates the process of discovering relevant
internship opportunities across multiple Indian job platforms.

Usage:
    python internhunt.py                    # Run without resume
    python internhunt.py resume.pdf         # Run with resume parsing
    python internhunt.py --help             # Show help message

Author: InternHunt Team
License: MIT
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.main import InternHuntApp
from src.logging_config import get_logger


logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog='internhunt',
        description='InternHunt v6 - Automated Internship Discovery',
        epilog='''
Examples:
  %(prog)s                    Run without resume parsing
  %(prog)s resume.pdf         Run with resume parsing
  %(prog)s --version          Show version information

For more information, visit: https://github.com/internhunt/internhunt-v6
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Optional resume path argument
    parser.add_argument(
        'resume',
        nargs='?',
        type=str,
        default=None,
        help='Path to PDF resume file (optional). If provided, skills will be extracted automatically.'
    )
    
    # Version flag
    parser.add_argument(
        '--version',
        action='version',
        version='InternHunt v6.0.0',
        help='Show version information and exit'
    )
    
    return parser


def validate_resume_path(resume_path_str: str) -> Path:
    """
    Validate the resume file path.
    
    Args:
        resume_path_str: Resume file path as string
        
    Returns:
        Path: Validated Path object
        
    Raises:
        SystemExit: If validation fails
    """
    resume_path = Path(resume_path_str)
    
    # Check if file exists
    if not resume_path.exists():
        print(f"Error: Resume file not found: {resume_path}")
        print(f"Please check the file path and try again.")
        sys.exit(1)
    
    # Check if it's a file (not a directory)
    if not resume_path.is_file():
        print(f"Error: Path is not a file: {resume_path}")
        sys.exit(1)
    
    # Check if it's a PDF file
    if resume_path.suffix.lower() != '.pdf':
        print(f"Warning: File does not have .pdf extension: {resume_path}")
        print(f"Attempting to parse anyway...")
    
    return resume_path


def main():
    """
    Main entry point for InternHunt CLI application.
    
    Handles:
    - Command-line argument parsing
    - Resume path validation
    - Application initialization and execution
    - Keyboard interrupts (Ctrl+C)
    - Unexpected errors
    """
    try:
        # Parse command-line arguments
        parser = create_parser()
        args = parser.parse_args()
        
        # Validate resume path if provided
        resume_path = None
        if args.resume:
            resume_path = validate_resume_path(args.resume)
            logger.info(f"Resume path provided: {resume_path}")
        else:
            logger.info("No resume path provided, skipping resume parsing")
        
        # Create and run the application
        app = InternHuntApp()
        app.run(resume_path)
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        logger.info("Application interrupted by user (Ctrl+C)")
        print("\n\nInternHunt interrupted. Goodbye!")
        sys.exit(0)
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in CLI entry point: {e}", exc_info=True)
        print(f"\nAn unexpected error occurred: {e}")
        print("Check internhunt.log for detailed error information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
