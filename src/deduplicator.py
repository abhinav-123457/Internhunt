"""
Deduplicator Module

Removes duplicate internship listings based on normalized title and company name.
Retains the highest scored duplicate and maintains sorted order.
"""

import re
import logging
from typing import List, Dict

from .scoring_engine import ScoredListing
from .logging_config import get_logger


logger = get_logger(__name__)


class Deduplicator:
    """
    Removes duplicate job listings based on normalized title and company.
    
    Deduplication strategy:
    - Normalize text: lowercase, strip whitespace, remove special characters
    - Key: "{normalized_title}::{normalized_company}"
    - Conflict resolution: Keep listing with highest score
    - Preserve order: Maintain sorted order after deduplication
    """
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for comparison.
        
        Normalization steps:
        1. Convert to lowercase using Unicode case-folding
        2. Strip leading/trailing whitespace
        3. Remove special characters (keep only alphanumeric and spaces)
        4. Collapse multiple spaces to single space
        
        Args:
            text: Text to normalize
            
        Returns:
            str: Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase using casefold() for proper Unicode handling
        # casefold() handles special cases like German 'ß' -> 'ss'
        normalized = text.casefold()
        
        # Strip whitespace
        normalized = normalized.strip()
        
        # Remove special characters (keep alphanumeric and spaces)
        # Use Unicode-aware character classes
        normalized = re.sub(r'[^\w\s]', '', normalized, flags=re.UNICODE)
        
        # Collapse multiple spaces to single space
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    @staticmethod
    def _generate_key(listing: ScoredListing) -> str:
        """
        Generate unique key from normalized title and company.
        
        Args:
            listing: ScoredListing to generate key for
            
        Returns:
            str: Unique key in format "{title}::{company}"
        """
        normalized_title = Deduplicator.normalize_text(listing.listing.title)
        normalized_company = Deduplicator.normalize_text(listing.listing.company)
        
        return f"{normalized_title}::{normalized_company}"
    
    @staticmethod
    def deduplicate(listings: List[ScoredListing]) -> List[ScoredListing]:
        """
        Remove duplicates, keeping highest scored version.
        
        Maintains sorted order after deduplication (assumes input is sorted).
        
        Args:
            listings: List of ScoredListing objects (should be sorted by score)
            
        Returns:
            List[ScoredListing]: Deduplicated list maintaining sorted order
        """
        if not listings:
            return []
        
        logger.info(f"Deduplicating {len(listings)} listings")
        
        # Dictionary to track highest scored listing for each key
        seen: Dict[str, ScoredListing] = {}
        
        # Process listings in order (since they're sorted by score descending)
        for listing in listings:
            key = Deduplicator._generate_key(listing)
            
            # If we haven't seen this key, or this listing has higher score, keep it
            if key not in seen or listing.score > seen[key].score:
                if key in seen:
                    logger.debug(f"Replacing duplicate: '{listing.listing.title}' at {listing.listing.company} "
                               f"(old score: {seen[key].score:.1f}, new score: {listing.score:.1f})")
                seen[key] = listing
        
        # Convert back to list, maintaining order
        # Since input is sorted by score descending, we need to preserve that order
        deduplicated = []
        seen_keys = set()
        
        for listing in listings:
            key = Deduplicator._generate_key(listing)
            if key not in seen_keys:
                deduplicated.append(seen[key])
                seen_keys.add(key)
        
        duplicates_removed = len(listings) - len(deduplicated)
        logger.info(f"Removed {duplicates_removed} duplicates, {len(deduplicated)} unique listings remain")
        
        return deduplicated
