"""
Preference Wizard Module

Interactive CLI interface for collecting user search preferences.
Validates input and handles default values appropriately.
"""

import logging
from dataclasses import dataclass
from typing import List


logger = logging.getLogger(__name__)


@dataclass
class UserPreferences:
    """User search preferences collected from wizard"""
    wanted_keywords: List[str]
    reject_keywords: List[str]
    remote_preference: str  # 'yes', 'no', 'any'
    min_stipend: int
    max_post_age_days: int
    max_results: int
    preferred_locations: List[str]
    resume_skills: List[str]


class PreferenceWizard:
    """
    Interactive CLI wizard for collecting user search preferences.
    
    Prompts user for various search criteria with validation and default values.
    """
    
    def __init__(self):
        """Initialize the preference wizard"""
        logger.info("Initializing PreferenceWizard")
    
    def run_wizard(self, resume_skills: List[str] = None) -> UserPreferences:
        """
        Run the interactive preference wizard.
        
        Args:
            resume_skills: Optional list of skills extracted from resume
            
        Returns:
            UserPreferences object with collected preferences
        """
        logger.info("Starting preference wizard")
        
        print("\n" + "="*60)
        print("InternHunt v6 - Preference Wizard")
        print("="*60)
        print("\nLet's customize your internship search!\n")
        
        # Collect preferences
        wanted_keywords = self._prompt_keywords(
            "Enter wanted keywords (comma-separated, e.g., 'python, machine learning, data science'): "
        )
        
        reject_keywords = self._prompt_keywords(
            "Enter reject keywords (comma-separated, leave empty for none): ",
            allow_empty=True
        )
        
        # Set remote preference to 'any' (no filtering by remote)
        remote_preference = 'any'
        
        # Set minimum stipend to 0 (no filtering by stipend)
        min_stipend = 0
        
        max_post_age_days = self._prompt_integer(
            "Enter maximum post age in days (e.g., 30): ",
            default=30,
            min_val=1
        )
        
        max_results = self._prompt_integer(
            "Enter maximum number of results (default 100): ",
            default=100,
            min_val=1
        )
        
        # Don't ask for locations - show all locations
        preferred_locations = []
        
        # Use resume skills if provided, otherwise empty list
        skills = resume_skills if resume_skills else []
        
        preferences = UserPreferences(
            wanted_keywords=wanted_keywords,
            reject_keywords=reject_keywords,
            remote_preference=remote_preference,
            min_stipend=min_stipend,
            max_post_age_days=max_post_age_days,
            max_results=max_results,
            preferred_locations=preferred_locations,
            resume_skills=skills
        )
        
        logger.info(f"Preferences collected: {len(wanted_keywords)} wanted keywords, "
                   f"{len(reject_keywords)} reject keywords, "
                   f"remote={remote_preference}, min_stipend={min_stipend}")
        
        print("\n" + "="*60)
        print("Preferences saved! Starting internship search...")
        print("="*60 + "\n")
        
        return preferences
    
    def _prompt_keywords(self, prompt: str, allow_empty: bool = False) -> List[str]:
        """
        Prompt for comma-separated keywords.
        
        Args:
            prompt: Prompt message to display
            allow_empty: Whether to allow empty input
            
        Returns:
            List of keywords (lowercase, stripped)
        """
        while True:
            try:
                user_input = input(prompt).strip()
                
                # Handle empty input
                if not user_input:
                    if allow_empty:
                        return []
                    else:
                        print("Error: This field cannot be empty. Please enter at least one keyword.")
                        continue
                
                # Parse comma-separated values
                keywords = [kw.strip().lower() for kw in user_input.split(',') if kw.strip()]
                
                if not keywords and not allow_empty:
                    print("Error: This field cannot be empty. Please enter at least one keyword.")
                    continue
                
                return keywords
                
            except KeyboardInterrupt:
                print("\n\nWizard interrupted by user.")
                raise
            except Exception as e:
                logger.error(f"Error parsing keywords: {e}")
                print(f"Error: Invalid input. Please try again.")
    
    def _prompt_remote_preference(self) -> str:
        """
        Prompt for remote work preference.
        
        Returns:
            One of 'yes', 'no', or 'any'
        """
        while True:
            try:
                user_input = input("Remote work preference (yes/no/any): ").strip().lower()
                
                if user_input in ['yes', 'no', 'any']:
                    return user_input
                else:
                    print("Error: Please enter 'yes', 'no', or 'any'.")
                    
            except KeyboardInterrupt:
                print("\n\nWizard interrupted by user.")
                raise
            except Exception as e:
                logger.error(f"Error parsing remote preference: {e}")
                print(f"Error: Invalid input. Please try again.")
    
    def _prompt_integer(self, prompt: str, default: int, min_val: int = 0) -> int:
        """
        Prompt for integer value with validation.
        
        Args:
            prompt: Prompt message to display
            default: Default value if user presses Enter
            min_val: Minimum allowed value
            
        Returns:
            Validated integer value
        """
        while True:
            try:
                user_input = input(prompt).strip()
                
                # Handle empty input (use default)
                if not user_input:
                    return default
                
                # Parse integer
                value = int(user_input)
                
                # Validate minimum value
                if value < min_val:
                    if min_val == 0:
                        print(f"Error: Please enter a non-negative number (>= {min_val}).")
                    else:
                        print(f"Error: Please enter a positive number (>= {min_val}).")
                    continue
                
                return value
                
            except ValueError:
                print("Error: Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\nWizard interrupted by user.")
                raise
            except Exception as e:
                logger.error(f"Error parsing integer: {e}")
                print(f"Error: Invalid input. Please try again.")
