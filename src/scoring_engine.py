"""
Scoring Engine Module

Calculates relevance scores for internship listings based on user preferences.
Implements keyword scoring, skill matching, stipend scoring, remote detection,
location matching, and reject keyword filtering.
"""

import re
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional

from .scrapers.base_scraper import JobListing
from .preference_wizard import UserPreferences
from .logging_config import get_logger


logger = get_logger(__name__)


@dataclass
class ScoredListing:
    """Job listing with calculated relevance score"""
    listing: JobListing
    score: float
    score_breakdown: Dict[str, float]  # Component scores for transparency


class ScoringEngine:
    """
    Calculates relevance scores for job listings based on user preferences.
    
    Scoring components:
    - Keyword Score: 10 points per wanted keyword match (CRITICAL)
    - Skill Score: 3 points per resume skill match
    - Stipend Score: Proportional bonus (max 3 points)
    - Remote Score: 5 points if remote match and user wants remote
    - Location Score: 5 points for location match
    
    Rejection criteria:
    - Contains reject keyword
    - Zero keyword matches (when keywords specified)
    
    Note: Stipend is NOT used for filtering - all stipend levels shown.
    Listings must match at least one keyword to be relevant.
    """
    
    # Keyword expansion map for common abbreviations
    KEYWORD_EXPANSIONS = {
        'ml': ['ml', 'machine learning'],
        'ai': ['ai', 'artificial intelligence'],
        'nlp': ['nlp', 'natural language processing'],
        'cv': ['cv', 'computer vision'],
        'dl': ['dl', 'deep learning'],
        'ds': ['ds', 'data science'],
        'da': ['da', 'data analytics', 'data analysis'],
        'bi': ['bi', 'business intelligence'],
        'api': ['api', 'application programming interface'],
        'ui': ['ui', 'user interface'],
        'ux': ['ux', 'user experience'],
        'db': ['db', 'database'],
        'devops': ['devops', 'dev ops'],
        'sde': ['sde', 'software development engineer', 'software developer'],
        'swe': ['swe', 'software engineer'],
        'qa': ['qa', 'quality assurance'],
        'genai': ['genai', 'gen ai', 'generative ai', 'generative artificial intelligence'],
        'llm': ['llm', 'large language model'],
        'gpt': ['gpt', 'generative pre-trained transformer'],
        'software development': ['software development', 'software dev', 'software engineering'],
        'data science': ['data science', 'data scientist'],
        'machine learning': ['machine learning', 'ml'],
    }
    
    # Regex patterns for remote work detection (case-insensitive)
    REMOTE_PATTERNS = [
        r'\bremote\b',
        r'\bwfh\b',
        r'\bwork from home\b',
        r'\bwork-from-home\b',
        r'\bpan india\b',
        r'\bpan-india\b',
        r'\banywhere in india\b'
    ]
    
    def __init__(self, preferences: UserPreferences):
        """
        Initialize the scoring engine with user preferences.
        
        Args:
            preferences: UserPreferences object with search criteria
        """
        self.preferences = preferences
        
        # Expand keywords with their full forms
        self.expanded_keywords = self._expand_keywords(preferences.wanted_keywords)
        self.expanded_reject_keywords = self._expand_keywords(preferences.reject_keywords)
        
        # Compile remote patterns for efficiency
        self.remote_regex = re.compile(
            '|'.join(self.REMOTE_PATTERNS),
            re.IGNORECASE
        )
        
        logger.info(f"Initialized ScoringEngine with {len(preferences.wanted_keywords)} wanted keywords "
                   f"(expanded to {len(self.expanded_keywords)}), "
                   f"{len(preferences.reject_keywords)} reject keywords")
    
    def _expand_keywords(self, keywords: List[str]) -> List[str]:
        """
        Expand keywords with their full forms.
        
        For example: 'ml' -> ['ml', 'machine learning']
        
        Args:
            keywords: List of keywords to expand
            
        Returns:
            List[str]: Expanded list of keywords
        """
        expanded = []
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            
            # Add the original keyword
            expanded.append(keyword_lower)
            
            # Add expansions if available
            if keyword_lower in self.KEYWORD_EXPANSIONS:
                for expansion in self.KEYWORD_EXPANSIONS[keyword_lower]:
                    if expansion != keyword_lower:  # Don't duplicate
                        expanded.append(expansion)
                        logger.debug(f"Expanded '{keyword}' to include '{expansion}'")
        
        return list(set(expanded))  # Remove duplicates
    
    def score_listing(self, listing: JobListing) -> Optional[ScoredListing]:
        """
        Score a single listing based on preferences.
        
        Returns None if listing should be rejected (contains reject keyword).
        
        Args:
            listing: JobListing to score
            
        Returns:
            Optional[ScoredListing]: Scored listing or None if rejected
        """
        # Check reject keywords first
        if self._check_reject_keywords(listing):
            logger.debug(f"Listing rejected due to reject keyword: {listing.title}")
            return None
        
        # Note: Stipend filtering removed - show all listings regardless of stipend
        # The stipend will still be displayed in the dashboard
        
        # Calculate score components
        keyword_score = self._score_keywords(listing)
        
        # IMPORTANT: Reject if zero keyword matches when keywords are specified
        # This prevents completely irrelevant listings from appearing
        if self.preferences.wanted_keywords and keyword_score == 0:
            logger.debug(f"Listing rejected due to zero keyword matches: {listing.title}")
            return None
        skill_score = self._score_skills(listing)
        stipend_score = self._score_stipend(listing)
        remote_score = self._score_remote(listing)
        location_score = self._score_location(listing)
        
        # Calculate total score
        total_score = keyword_score + skill_score + stipend_score + remote_score + location_score
        
        # Create score breakdown for transparency
        score_breakdown = {
            'keyword': keyword_score,
            'skill': skill_score,
            'stipend': stipend_score,
            'remote': remote_score,
            'location': location_score
        }
        
        logger.debug(f"Scored listing: {listing.title} - Total: {total_score:.1f} "
                    f"(kw:{keyword_score}, sk:{skill_score}, st:{stipend_score:.1f}, "
                    f"rm:{remote_score}, loc:{location_score})")
        
        return ScoredListing(
            listing=listing,
            score=total_score,
            score_breakdown=score_breakdown
        )
    
    def score_all(self, listings: List[JobListing], min_score: float = 0.0) -> List[ScoredListing]:
        """
        Score all listings and sort by score in descending order.
        
        Args:
            listings: List of JobListing objects to score
            min_score: Minimum score threshold (default: 0.0 - show all)
            
        Returns:
            List[ScoredListing]: Scored listings sorted by score (highest first)
        """
        logger.info(f"Scoring {len(listings)} listings (showing all listings)")
        
        scored_listings = []
        rejected_count = 0
        
        for listing in listings:
            scored = self.score_listing(listing)
            if scored is None:
                rejected_count += 1
            else:
                scored_listings.append(scored)
        
        # Sort by score in descending order
        scored_listings.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"Scored {len(scored_listings)} listings, rejected {rejected_count} (reject keywords only)")
        
        return scored_listings
    
    def _check_reject_keywords(self, listing: JobListing) -> bool:
        """
        Check if listing contains any reject keywords using word boundary matching.
        Uses expanded keywords (e.g., 'ml' checks for both 'ml' and 'machine learning').
        
        Args:
            listing: JobListing to check
            
        Returns:
            bool: True if listing should be rejected, False otherwise
        """
        if not self.expanded_reject_keywords:
            return False
        
        # Combine title and description for searching
        searchable_text = f"{listing.title} {listing.description}".lower()
        
        # Check each expanded reject keyword with word boundary matching
        import re
        for keyword in self.expanded_reject_keywords:
            # Use word boundary regex to avoid partial matches
            # e.g., "hr" won't match "three" or "through"
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, searchable_text):
                logger.debug(f"Reject keyword '{keyword}' found in: {listing.title}")
                return True
        
        return False
    
    def _score_keywords(self, listing: JobListing) -> float:
        """
        Score based on wanted keyword matches (10 points per match) using word boundary matching.
        Uses expanded keywords (e.g., 'ml' checks for both 'ml' and 'machine learning').
        
        Args:
            listing: JobListing to score
            
        Returns:
            float: Keyword score
        """
        if not self.expanded_keywords:
            return 0.0
        
        # Combine title and description for searching
        searchable_text = f"{listing.title} {listing.description}".lower()
        
        # Count keyword matches with word boundary matching
        import re
        matches = 0
        matched_keywords = []
        for keyword in self.expanded_keywords:
            # Use word boundary regex for more accurate matching
            # This prevents "ai" from matching "email" or "said"
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, searchable_text):
                matches += 1
                matched_keywords.append(keyword)
        
        score = matches * 10.0  # 10 points per keyword match
        
        if matches > 0:
            logger.debug(f"Keyword matches for '{listing.title}': {matched_keywords} -> {score} points")
        
        return score
    
    def _score_skills(self, listing: JobListing) -> float:
        """
        Score based on resume skill matches (3 points per match).
        
        Args:
            listing: JobListing to score
            
        Returns:
            float: Skill score
        """
        if not self.preferences.resume_skills:
            return 0.0
        
        # Combine title and description for searching
        searchable_text = f"{listing.title} {listing.description}".lower()
        
        # Count skill matches
        matches = 0
        for skill in self.preferences.resume_skills:
            # Use word boundary regex for more accurate matching
            skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(skill_pattern, searchable_text):
                matches += 1
        
        score = matches * 3.0  # Increased from 1.0 to 3.0
        
        if matches > 0:
            logger.debug(f"Skill matches for '{listing.title}': {matches} skills -> {score} points")
        
        return score
    
    def _score_stipend(self, listing: JobListing) -> float:
        """
        Score based on stipend amount (proportional bonus, max 3 points).
        
        Formula: min((stipend - min_stipend) / 10000, 3)
        
        Args:
            listing: JobListing to score
            
        Returns:
            float: Stipend score (0-3 points)
        """
        if listing.stipend is None:
            return 0.0
        
        if listing.stipend <= self.preferences.min_stipend:
            return 0.0
        
        # Calculate proportional score (reduced max from 5 to 3)
        stipend_above_min = listing.stipend - self.preferences.min_stipend
        score = min(stipend_above_min / 10000.0, 3.0)
        
        logger.debug(f"Stipend score for '{listing.title}': ₹{listing.stipend} -> {score:.2f} points")
        
        return score
    
    def _score_remote(self, listing: JobListing) -> float:
        """
        Score based on remote work indicators (5 points if match and user wants remote).
        
        Uses regex patterns to detect remote work indicators in location and description.
        
        Args:
            listing: JobListing to score
            
        Returns:
            float: Remote score (0 or 5 points)
        """
        # Only score if user wants remote work
        if self.preferences.remote_preference != 'yes':
            return 0.0
        
        # Check location and description for remote indicators
        searchable_text = f"{listing.location} {listing.description}".lower()
        
        if self.remote_regex.search(searchable_text):
            logger.debug(f"Remote work detected for '{listing.title}'")
            return 5.0
        
        return 0.0
    
    def _score_location(self, listing: JobListing) -> float:
        """
        Score based on location match (5 points for match).
        
        Args:
            listing: JobListing to score
            
        Returns:
            float: Location score (0 or 5 points)
        """
        if not self.preferences.preferred_locations:
            return 0.0
        
        listing_location = listing.location.lower()
        
        # Check if any preferred location is in the listing location
        for preferred_loc in self.preferences.preferred_locations:
            if preferred_loc in listing_location:
                logger.debug(f"Location match for '{listing.title}': {preferred_loc}")
                return 5.0
        
        return 0.0
