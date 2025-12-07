"""
Property-Based Tests for Resume Parser

Tests universal properties that should hold across all valid resume inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import tempfile
import os

from src.resume_parser import ResumeParser, ResumeSkills


# Reuse parser instance to avoid reloading the model for each test
_parser_instance = None


def get_parser():
    """Get or create a singleton parser instance"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = ResumeParser()
    return _parser_instance


# **Feature: internhunt-v6, Property 1: Resume skill extraction bounds**
# **Validates: Requirements 1.3**
@settings(max_examples=100, deadline=None)
@given(
    resume_text=st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
        min_size=100,
        max_size=5000
    )
)
def test_skill_extraction_bounds(resume_text):
    """
    Property: For any valid resume text, the number of extracted skills 
    should be between 10 and 50 inclusive.
    
    This property ensures that the skill matching algorithm always returns
    a reasonable number of skills regardless of resume content.
    """
    parser = get_parser()
    
    # Match skills from the generated resume text
    result = parser.match_skills(resume_text)
    
    # Verify the property: 10 <= number of skills <= 50
    num_skills = len(result.extracted_skills)
    assert 10 <= num_skills <= 50, (
        f"Expected 10-50 skills, but got {num_skills} skills. "
        f"Skills: {result.extracted_skills}"
    )
    
    # Additional invariants
    assert len(result.extracted_skills) == len(result.confidence_scores), (
        "Number of skills should match number of confidence scores"
    )
    
    # All extracted skills should be from the skill library
    skill_library_set = set(parser.skill_library)
    for skill in result.extracted_skills:
        assert skill in skill_library_set, (
            f"Skill '{skill}' not found in skill library"
        )
    
    # Confidence scores should be between 0 and 1
    for skill, score in result.confidence_scores.items():
        assert 0 <= score <= 1, (
            f"Confidence score for '{skill}' is {score}, expected 0-1"
        )
