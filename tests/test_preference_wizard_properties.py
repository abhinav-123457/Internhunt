"""
Property-Based Tests for Preference Wizard

Tests input validation properties using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import patch, MagicMock
from io import StringIO

from src.preference_wizard import PreferenceWizard, UserPreferences


# **Feature: internhunt-v6, Property 2: Preference wizard input validation**
# **Validates: Requirements 2.4, 2.5, 2.6, 8.3**


@settings(max_examples=100)
@given(
    stipend=st.integers(min_value=-1000, max_value=-1)
)
def test_negative_stipend_rejected(stipend):
    """
    Property: For any negative stipend value, the wizard should reject it
    and re-prompt for valid input.
    
    This tests that the _prompt_integer method properly validates non-negative
    stipend values as per Requirements 2.4.
    """
    wizard = PreferenceWizard()
    
    # Mock input to provide negative value first, then valid value
    with patch('builtins.input', side_effect=[str(stipend), '0']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = wizard._prompt_integer("Enter stipend: ", default=0, min_val=0)
            
            # Should return the valid value (0) after rejecting negative
            assert result == 0
            
            # Should have printed an error message
            output = mock_stdout.getvalue()
            assert "Error" in output or "non-negative" in output.lower()


@settings(max_examples=100)
@given(
    post_age=st.integers(min_value=-1000, max_value=0)
)
def test_non_positive_post_age_rejected(post_age):
    """
    Property: For any non-positive post age value, the wizard should reject it
    and re-prompt for valid input.
    
    This tests that the _prompt_integer method properly validates positive
    post age values as per Requirements 2.5.
    """
    wizard = PreferenceWizard()
    
    # Mock input to provide non-positive value first, then valid value
    with patch('builtins.input', side_effect=[str(post_age), '30']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = wizard._prompt_integer("Enter post age: ", default=30, min_val=1)
            
            # Should return the valid value (30) after rejecting non-positive
            assert result == 30
            
            # Should have printed an error message
            output = mock_stdout.getvalue()
            assert "Error" in output or "positive" in output.lower()


@settings(max_examples=100)
@given(
    max_results=st.integers(min_value=-1000, max_value=0)
)
def test_non_positive_max_results_rejected(max_results):
    """
    Property: For any non-positive max results value, the wizard should reject it
    and re-prompt for valid input.
    
    This tests that the _prompt_integer method properly validates positive
    max results values as per Requirements 2.6.
    """
    wizard = PreferenceWizard()
    
    # Mock input to provide non-positive value first, then valid value
    with patch('builtins.input', side_effect=[str(max_results), '50']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = wizard._prompt_integer("Enter max results: ", default=50, min_val=1)
            
            # Should return the valid value (50) after rejecting non-positive
            assert result == 50
            
            # Should have printed an error message
            output = mock_stdout.getvalue()
            assert "Error" in output or "positive" in output.lower()


@settings(max_examples=100)
@given(
    invalid_remote=st.text(min_size=1).filter(
        lambda x: x.strip().lower() not in ['yes', 'no', 'any']
    )
)
def test_invalid_remote_preference_rejected(invalid_remote):
    """
    Property: For any remote preference value that is not 'yes', 'no', or 'any',
    the wizard should reject it and re-prompt for valid input.
    
    This tests that the _prompt_remote_preference method properly validates
    remote preference values as per Requirements 2.3 and 8.3.
    """
    wizard = PreferenceWizard()
    
    # Mock input to provide invalid value first, then valid value
    with patch('builtins.input', side_effect=[invalid_remote, 'any']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = wizard._prompt_remote_preference()
            
            # Should return the valid value ('any') after rejecting invalid
            assert result == 'any'
            
            # Should have printed an error message
            output = mock_stdout.getvalue()
            assert "Error" in output


@settings(max_examples=100)
@given(
    valid_remote=st.sampled_from(['yes', 'no', 'any', 'YES', 'NO', 'ANY', 'Yes', 'No', 'Any'])
)
def test_valid_remote_preference_accepted(valid_remote):
    """
    Property: For any valid remote preference value (yes/no/any in any case),
    the wizard should accept it and return the lowercase version.
    
    This tests that the _prompt_remote_preference method properly accepts
    valid remote preference values as per Requirements 2.3.
    """
    wizard = PreferenceWizard()
    
    # Mock input to provide valid value
    with patch('builtins.input', return_value=valid_remote):
        result = wizard._prompt_remote_preference()
        
        # Should return the lowercase version
        assert result in ['yes', 'no', 'any']
        assert result == valid_remote.lower()


@settings(max_examples=100)
@given(
    valid_stipend=st.integers(min_value=0, max_value=100000)
)
def test_valid_stipend_accepted(valid_stipend):
    """
    Property: For any non-negative stipend value, the wizard should accept it.
    
    This tests that the _prompt_integer method properly accepts valid
    stipend values as per Requirements 2.4.
    """
    wizard = PreferenceWizard()
    
    # Mock input to provide valid stipend
    with patch('builtins.input', return_value=str(valid_stipend)):
        result = wizard._prompt_integer("Enter stipend: ", default=0, min_val=0)
        
        # Should return the provided value
        assert result == valid_stipend


@settings(max_examples=100)
@given(
    valid_post_age=st.integers(min_value=1, max_value=365)
)
def test_valid_post_age_accepted(valid_post_age):
    """
    Property: For any positive post age value, the wizard should accept it.
    
    This tests that the _prompt_integer method properly accepts valid
    post age values as per Requirements 2.5.
    """
    wizard = PreferenceWizard()
    
    # Mock input to provide valid post age
    with patch('builtins.input', return_value=str(valid_post_age)):
        result = wizard._prompt_integer("Enter post age: ", default=30, min_val=1)
        
        # Should return the provided value
        assert result == valid_post_age


@settings(max_examples=100)
@given(
    non_integer=st.text(min_size=1).filter(
        lambda x: not x.strip().isdigit() and x.strip() != '' and not (x.strip().startswith('-') and x.strip()[1:].isdigit())
    )
)
def test_non_integer_input_rejected(non_integer):
    """
    Property: For any non-integer input to integer prompts, the wizard should
    reject it and re-prompt for valid input.
    
    This tests that the _prompt_integer method properly validates integer
    input as per Requirements 8.3.
    """
    wizard = PreferenceWizard()
    
    # Mock input to provide non-integer first, then valid value
    with patch('builtins.input', side_effect=[non_integer, '50']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = wizard._prompt_integer("Enter value: ", default=50, min_val=0)
            
            # Should return the valid value (50) after rejecting non-integer
            assert result == 50
            
            # Should have printed an error message
            output = mock_stdout.getvalue()
            assert "Error" in output or "valid number" in output.lower()


@settings(max_examples=100)
@given(
    keywords=st.lists(
        st.text(min_size=1, max_size=20).filter(lambda x: ',' not in x and x.strip()),
        min_size=1,
        max_size=10
    )
)
def test_keyword_parsing_consistency(keywords):
    """
    Property: For any list of keywords provided as comma-separated values,
    the wizard should parse them correctly into a list.
    
    This tests that the _prompt_keywords method properly parses comma-separated
    values as per Requirements 2.1 and 2.2.
    
    Note: Keywords cannot contain commas as comma is the delimiter.
    """
    wizard = PreferenceWizard()
    
    # Create comma-separated input
    input_str = ', '.join(keywords)
    
    # Mock input
    with patch('builtins.input', return_value=input_str):
        result = wizard._prompt_keywords("Enter keywords: ", allow_empty=False)
        
        # Should return list with same number of keywords (after stripping)
        assert len(result) == len(keywords)
        
        # All keywords should be lowercase and stripped
        for kw in result:
            assert kw == kw.lower()
            assert kw == kw.strip()
