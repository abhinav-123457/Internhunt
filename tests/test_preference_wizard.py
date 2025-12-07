"""
Unit Tests for Preference Wizard

Tests keyword parsing, default value handling, and empty input handling.
"""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

from src.preference_wizard import PreferenceWizard, UserPreferences


class TestKeywordParsing:
    """Test keyword parsing with comma-separated values (Requirements 2.1, 2.2)"""
    
    def test_single_keyword(self):
        """Test parsing a single keyword"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='python'):
            result = wizard._prompt_keywords("Enter keywords: ")
            
        assert result == ['python']
    
    def test_multiple_keywords(self):
        """Test parsing multiple comma-separated keywords"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='python, java, javascript'):
            result = wizard._prompt_keywords("Enter keywords: ")
            
        assert result == ['python', 'java', 'javascript']
    
    def test_keywords_with_extra_spaces(self):
        """Test parsing keywords with extra whitespace"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='  python  ,  java  ,  javascript  '):
            result = wizard._prompt_keywords("Enter keywords: ")
            
        assert result == ['python', 'java', 'javascript']
    
    def test_keywords_case_normalization(self):
        """Test that keywords are converted to lowercase"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='Python, JAVA, JavaScript'):
            result = wizard._prompt_keywords("Enter keywords: ")
            
        assert result == ['python', 'java', 'javascript']
    
    def test_empty_keywords_rejected_when_required(self):
        """Test that empty input is rejected when keywords are required"""
        wizard = PreferenceWizard()
        
        # First input is empty, second is valid
        with patch('builtins.input', side_effect=['', 'python']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = wizard._prompt_keywords("Enter keywords: ", allow_empty=False)
                
        assert result == ['python']
        output = mock_stdout.getvalue()
        assert 'Error' in output or 'empty' in output.lower()
    
    def test_empty_keywords_accepted_when_optional(self):
        """Test that empty input is accepted when keywords are optional"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value=''):
            result = wizard._prompt_keywords("Enter keywords: ", allow_empty=True)
            
        assert result == []
    
    def test_keywords_with_trailing_commas(self):
        """Test parsing keywords with trailing commas"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='python, java,'):
            result = wizard._prompt_keywords("Enter keywords: ")
            
        assert result == ['python', 'java']


class TestDefaultValueHandling:
    """Test default value handling for integer prompts (Requirements 2.6, 2.7)"""
    
    def test_empty_input_uses_default_stipend(self):
        """Test that empty input uses default value for stipend"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value=''):
            result = wizard._prompt_integer("Enter stipend: ", default=0, min_val=0)
            
        assert result == 0
    
    def test_empty_input_uses_default_max_results(self):
        """Test that empty input uses default value for max results"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value=''):
            result = wizard._prompt_integer("Enter max results: ", default=50, min_val=1)
            
        assert result == 50
    
    def test_empty_input_uses_default_post_age(self):
        """Test that empty input uses default value for post age"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value=''):
            result = wizard._prompt_integer("Enter post age: ", default=30, min_val=1)
            
        assert result == 30
    
    def test_explicit_value_overrides_default(self):
        """Test that explicit value overrides default"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='100'):
            result = wizard._prompt_integer("Enter value: ", default=50, min_val=0)
            
        assert result == 100


class TestEmptyInputHandling:
    """Test empty input handling for optional fields (Requirements 2.7)"""
    
    def test_empty_reject_keywords(self):
        """Test that empty reject keywords are accepted"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value=''):
            result = wizard._prompt_keywords("Enter reject keywords: ", allow_empty=True)
            
        assert result == []
    
    def test_empty_preferred_locations(self):
        """Test that empty preferred locations are accepted"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value=''):
            result = wizard._prompt_keywords("Enter locations: ", allow_empty=True)
            
        assert result == []
    
    def test_whitespace_only_treated_as_empty(self):
        """Test that whitespace-only input is treated as empty"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='   '):
            result = wizard._prompt_keywords("Enter keywords: ", allow_empty=True)
            
        assert result == []


class TestRemotePreference:
    """Test remote preference validation (Requirements 2.3)"""
    
    def test_yes_accepted(self):
        """Test that 'yes' is accepted"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='yes'):
            result = wizard._prompt_remote_preference()
            
        assert result == 'yes'
    
    def test_no_accepted(self):
        """Test that 'no' is accepted"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='no'):
            result = wizard._prompt_remote_preference()
            
        assert result == 'no'
    
    def test_any_accepted(self):
        """Test that 'any' is accepted"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='any'):
            result = wizard._prompt_remote_preference()
            
        assert result == 'any'
    
    def test_case_insensitive(self):
        """Test that remote preference is case-insensitive"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='YES'):
            result = wizard._prompt_remote_preference()
            
        assert result == 'yes'


class TestIntegerValidation:
    """Test integer validation (Requirements 2.4, 2.5, 2.6)"""
    
    def test_valid_positive_integer(self):
        """Test that valid positive integers are accepted"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='100'):
            result = wizard._prompt_integer("Enter value: ", default=50, min_val=1)
            
        assert result == 100
    
    def test_zero_accepted_for_stipend(self):
        """Test that zero is accepted for stipend (min_val=0)"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', return_value='0'):
            result = wizard._prompt_integer("Enter stipend: ", default=0, min_val=0)
            
        assert result == 0
    
    def test_negative_rejected_for_stipend(self):
        """Test that negative values are rejected for stipend"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', side_effect=['-100', '0']):
            with patch('sys.stdout', new_callable=StringIO):
                result = wizard._prompt_integer("Enter stipend: ", default=0, min_val=0)
                
        assert result == 0
    
    def test_zero_rejected_for_positive_fields(self):
        """Test that zero is rejected for fields requiring positive values"""
        wizard = PreferenceWizard()
        
        with patch('builtins.input', side_effect=['0', '30']):
            with patch('sys.stdout', new_callable=StringIO):
                result = wizard._prompt_integer("Enter post age: ", default=30, min_val=1)
                
        assert result == 30


class TestFullWizard:
    """Test complete wizard flow"""
    
    def test_run_wizard_with_all_inputs(self):
        """Test running the full wizard with all inputs provided"""
        wizard = PreferenceWizard()
        
        inputs = [
            'python, machine learning',  # wanted keywords
            'sales, marketing',          # reject keywords
            # remote preference removed - now hardcoded to 'any'
            # min stipend removed - now hardcoded to 0
            '30',                         # max post age
            '50',                         # max results
            # preferred locations removed - now hardcoded to []
        ]
        
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO):
                result = wizard.run_wizard(resume_skills=['python', 'java'])
                
        assert isinstance(result, UserPreferences)
        assert result.wanted_keywords == ['python', 'machine learning']
        assert result.reject_keywords == ['sales', 'marketing']
        assert result.remote_preference == 'any'  # Always 'any' now
        assert result.min_stipend == 0  # Always 0 now
        assert result.max_post_age_days == 30
        assert result.max_results == 50
        assert result.preferred_locations == []  # Always empty now
        assert result.resume_skills == ['python', 'java']
    
    def test_run_wizard_with_defaults(self):
        """Test running the wizard with default values"""
        wizard = PreferenceWizard()
        
        inputs = [
            'python',  # wanted keywords
            '',        # reject keywords (empty)
            'any',     # remote preference
            '',        # min stipend (default 0)
            '',        # max post age (default 30)
            '',        # max results (default 50)
            ''         # preferred locations (empty)
        ]
        
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO):
                result = wizard.run_wizard()
                
        assert result.wanted_keywords == ['python']
        assert result.reject_keywords == []
        assert result.remote_preference == 'any'
        assert result.min_stipend == 0
        assert result.max_post_age_days == 30
        assert result.max_results == 100  # Updated default from 50 to 100
        assert result.preferred_locations == []
        assert result.resume_skills == []
    
    def test_run_wizard_without_resume_skills(self):
        """Test running the wizard without resume skills"""
        wizard = PreferenceWizard()
        
        inputs = [
            'python',
            '',
            'any',
            '',
            '',
            '',
            ''
        ]
        
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=StringIO):
                result = wizard.run_wizard(resume_skills=None)
                
        assert result.resume_skills == []
