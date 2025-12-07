"""
Unit Tests for Resume Parser

Tests specific functionality and edge cases for the resume parser module.
"""

import pytest
from pathlib import Path
import tempfile
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

from src.resume_parser import ResumeParser, ResumeSkills


class TestResumeParser:
    """Unit tests for ResumeParser class"""
    
    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing"""
        return ResumeParser()
    
    def test_match_skills_returns_correct_bounds(self, parser):
        """Test that skill matching returns between 10-50 skills"""
        resume_text = """
        Software Engineer with 5 years of experience in Python, Java, and JavaScript.
        Proficient in machine learning, deep learning, and data science.
        Experience with React, Node.js, Django, and Flask frameworks.
        Strong knowledge of AWS, Docker, and Kubernetes.
        Skilled in SQL, PostgreSQL, and MongoDB databases.
        """
        
        result = parser.match_skills(resume_text)
        
        assert isinstance(result, ResumeSkills)
        assert 10 <= len(result.extracted_skills) <= 50
        assert len(result.extracted_skills) == len(result.confidence_scores)
    
    def test_match_skills_with_empty_text(self, parser):
        """Test that empty text returns empty results"""
        result = parser.match_skills("")
        
        assert isinstance(result, ResumeSkills)
        assert len(result.extracted_skills) == 0
        assert len(result.confidence_scores) == 0
    
    def test_match_skills_confidence_scores_in_range(self, parser):
        """Test that confidence scores are between 0 and 1"""
        resume_text = "Python developer with experience in machine learning and web development"
        
        result = parser.match_skills(resume_text)
        
        for skill, score in result.confidence_scores.items():
            assert 0 <= score <= 1, f"Score for {skill} is {score}, expected 0-1"
    
    def test_match_skills_returns_valid_skills(self, parser):
        """Test that all returned skills are from the skill library"""
        resume_text = "Experienced in Python, Java, React, and AWS cloud services"
        
        result = parser.match_skills(resume_text)
        
        skill_library_set = set(parser.skill_library)
        for skill in result.extracted_skills:
            assert skill in skill_library_set
    
    def test_extract_text_from_nonexistent_pdf(self, parser):
        """Test that nonexistent PDF raises ValueError"""
        fake_path = Path("nonexistent_file.pdf")
        
        with pytest.raises(ValueError, match="PDF file not found"):
            parser.extract_text_from_pdf(fake_path)
    
    def test_parse_resume_handles_errors_gracefully(self, parser):
        """Test that parse_resume returns None on errors"""
        fake_path = Path("nonexistent_file.pdf")
        
        result = parser.parse_resume(fake_path)
        
        assert result is None
