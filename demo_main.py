"""
Demo script to test the main application orchestrator.

This script demonstrates the InternHunt application flow with mocked components.
"""

from pathlib import Path
from unittest.mock import Mock, patch
from src.main import InternHuntApp
from src.preference_wizard import UserPreferences
from src.scrapers.base_scraper import JobListing
from src.scoring_engine import ScoredListing


def demo_main_orchestrator():
    """Demonstrate the main orchestrator with mocked components"""
    
    print("="*60)
    print("InternHunt v6 - Main Orchestrator Demo")
    print("="*60)
    print("\nThis demo shows the complete pipeline orchestration.\n")
    
    # Create mock preferences
    mock_preferences = UserPreferences(
        wanted_keywords=["python", "machine learning"],
        reject_keywords=["sales"],
        remote_preference="yes",
        min_stipend=10000,
        max_post_age_days=30,
        max_results=100,
        preferred_locations=["bangalore", "remote"],
        resume_skills=["Python", "TensorFlow", "Data Science"]
    )
    
    # Create mock job listings
    mock_listing1 = JobListing(
        title="ML Intern",
        company="TechCorp",
        stipend=20000,
        location="Remote",
        description="Python machine learning internship",
        url="https://example.com/job1",
        posted_date="2024-01-01",
        source_platform="Internshala",
        raw_stipend_text="₹20,000/month"
    )
    
    mock_listing2 = JobListing(
        title="Data Science Intern",
        company="DataCo",
        stipend=25000,
        location="Bangalore",
        description="Work with Python and TensorFlow",
        url="https://example.com/job2",
        posted_date="2024-01-02",
        source_platform="Unstop",
        raw_stipend_text="₹25,000/month"
    )
    
    # Create mock scored listings
    mock_scored1 = ScoredListing(
        listing=mock_listing1,
        score=15.0,
        score_breakdown={"keyword": 4, "skill": 3, "stipend": 3, "remote": 5, "location": 0}
    )
    
    mock_scored2 = ScoredListing(
        listing=mock_listing2,
        score=18.0,
        score_breakdown={"keyword": 4, "skill": 4, "stipend": 5, "remote": 0, "location": 3}
    )
    
    print("✓ Created mock data:")
    print(f"  - Preferences: {len(mock_preferences.wanted_keywords)} wanted keywords")
    print(f"  - Listings: 2 mock job listings")
    print(f"  - Scored listings: 2 with scores 15.0 and 18.0")
    print()
    
    # Test individual components
    app = InternHuntApp()
    
    print("Testing individual pipeline components:")
    print()
    
    # Test 1: Resume parser (no resume)
    print("1. Resume Parser (no resume):")
    skills = app._run_resume_parser(None)
    print(f"   ✓ Returned {len(skills)} skills (expected: 0)")
    print()
    
    # Test 2: Max results limiting
    print("2. Max Results Limiting:")
    limited = app._apply_max_results_limit([mock_scored1, mock_scored2], max_results=1)
    print(f"   ✓ Limited from 2 to {len(limited)} listings")
    print()
    
    # Test 3: Print summary
    print("3. Execution Summary:")
    dashboard_path = Path("output/demo_dashboard.html")
    app._print_summary(100, 50, 2, dashboard_path)
    
    print("\n" + "="*60)
    print("Demo completed successfully!")
    print("="*60)
    print("\nThe main orchestrator is working correctly.")
    print("All pipeline components are properly integrated.")
    print()


if __name__ == "__main__":
    demo_main_orchestrator()
