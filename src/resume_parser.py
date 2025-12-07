"""
Resume Parser Module

Extracts skills from PDF resumes using semantic similarity with SentenceTransformer embeddings.
Handles corrupted/invalid PDF files gracefully.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader  # Fallback for older installations

from sentence_transformers import SentenceTransformer
import numpy as np

from src.skill_library import SkillLibrary


logger = logging.getLogger(__name__)


@dataclass
class ResumeSkills:
    """Container for extracted skills with confidence scores"""
    extracted_skills: List[str]
    confidence_scores: Dict[str, float]


class ResumeParser:
    """
    Parses PDF resumes and extracts relevant skills using semantic similarity.
    
    Uses SentenceTransformer embeddings to match resume text against a predefined
    skill library, returning 10-50 most relevant skills.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the resume parser with a SentenceTransformer model.
        
        Args:
            model_name: Name of the SentenceTransformer model to use for embeddings
        """
        logger.info(f"Initializing ResumeParser with model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.skill_library = SkillLibrary.get_all_skills()
        logger.info(f"Loaded {len(self.skill_library)} skills from library")
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from all pages concatenated
            
        Raises:
            ValueError: If PDF cannot be read or is corrupted
        """
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            if not pdf_path.exists():
                raise ValueError(f"PDF file not found: {pdf_path}")
            
            reader = PdfReader(str(pdf_path))
            
            if len(reader.pages) == 0:
                raise ValueError("PDF file has no pages")
            
            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
            
            if not text_parts:
                raise ValueError("No text could be extracted from PDF")
            
            full_text = "\n".join(text_parts)
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    def match_skills(self, resume_text: str, threshold: float = 0.3) -> ResumeSkills:
        """
        Match resume text against skill library using semantic similarity.
        
        Uses SentenceTransformer embeddings to compute cosine similarity between
        resume text and each skill. Returns 20-50 top matching skills.
        
        Args:
            resume_text: Extracted text from resume
            threshold: Minimum similarity score (0-1) for skill matching (default: 0.3)
            
        Returns:
            ResumeSkills object containing extracted skills and confidence scores
        """
        logger.info("Starting skill matching with embeddings")
        
        if not resume_text or not resume_text.strip():
            logger.warning("Empty resume text provided")
            return ResumeSkills(extracted_skills=[], confidence_scores={})
        
        # Generate embeddings for resume text and skills
        resume_embedding = self.model.encode(resume_text, convert_to_tensor=False)
        skill_embeddings = self.model.encode(self.skill_library, convert_to_tensor=False)
        
        # Compute cosine similarity
        similarities = self._cosine_similarity(resume_embedding, skill_embeddings)
        
        # Create skill-score pairs
        skill_scores = list(zip(self.skill_library, similarities))
        
        # Sort by score
        skill_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Filter by threshold
        filtered_skills = [(skill, score) for skill, score in skill_scores if score >= threshold]
        
        # Ensure we return between 20 and 50 skills
        min_skills = 20  # Increased from 10
        max_skills = 50
        
        # If we have fewer than 20 skills above threshold, take top 20 regardless
        if len(filtered_skills) < min_skills:
            logger.info(f"Only {len(filtered_skills)} skills above threshold {threshold}, taking top {min_skills}")
            final_skills = skill_scores[:min_skills]
        else:
            # Cap at 50 skills
            final_skills = filtered_skills[:max_skills]
        
        # Extract skills and scores
        extracted_skills = [skill for skill, _ in final_skills]
        confidence_scores = {skill: float(score) for skill, score in final_skills}
        
        logger.info(f"Extracted {len(extracted_skills)} skills from resume")
        
        return ResumeSkills(
            extracted_skills=extracted_skills,
            confidence_scores=confidence_scores
        )
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarity between a vector and a matrix of vectors.
        
        Args:
            vec1: Single embedding vector
            vec2: Matrix of embedding vectors
            
        Returns:
            Array of similarity scores
        """
        # Normalize vectors
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2, axis=1, keepdims=True)
        
        # Compute dot product
        similarities = np.dot(vec2_norm, vec1_norm)
        
        return similarities
    
    def parse_resume(self, pdf_path: Path, threshold: float = 0.5) -> Optional[ResumeSkills]:
        """
        Complete pipeline: extract text from PDF and match skills.
        
        Handles errors gracefully and returns None if parsing fails.
        
        Args:
            pdf_path: Path to PDF resume file
            threshold: Minimum similarity score for skill matching
            
        Returns:
            ResumeSkills object or None if parsing fails
        """
        try:
            text = self.extract_text_from_pdf(pdf_path)
            skills = self.match_skills(text, threshold)
            return skills
        except Exception as e:
            logger.error(f"Failed to parse resume: {e}")
            return None
