"""
Custom exception classes for ResumeScreener-AI.

This module defines the exception hierarchy for the ResumeScreener-AI system,
providing structured error handling with clear error messages and context.
"""

from typing import List, Optional, Set


class ResumeScreenerError(Exception):
    """
    Base exception class for all ResumeScreener-AI errors.
    
    This is the root of the exception hierarchy. All custom exceptions
    in the ResumeScreener-AI system should inherit from this class.
    
    Attributes:
        message: Human-readable error description
    """
    
    def __init__(self, message: str) -> None:
        """
        Initialize the base exception.
        
        Args:
            message: Human-readable error description
        """
        self.message = message
        super().__init__(self.message)


class DataValidationError(ResumeScreenerError):
    """
    Raised when input data validation fails.
    
    This exception is raised when required data is missing, malformed,
    or does not meet validation criteria (e.g., missing DataFrame columns,
    invalid data types, empty required fields).
    
    Attributes:
        message: Human-readable error description
        missing_columns: List of column names that are missing from the DataFrame
    """
    
    def __init__(self, message: str, missing_columns: Optional[List[str]] = None) -> None:
        """
        Initialize the data validation error.
        
        Args:
            message: Human-readable error description
            missing_columns: Optional list of missing column names
        """
        self.missing_columns = missing_columns or []
        
        # Enhance message with missing columns if provided
        if self.missing_columns:
            column_list = ", ".join(f"'{col}'" for col in self.missing_columns)
            enhanced_message = f"{message}. Missing columns: {column_list}"
        else:
            enhanced_message = message
            
        super().__init__(enhanced_message)


class SkillExtractionError(ResumeScreenerError):
    """
    Raised when skill extraction from text fails.
    
    This exception is raised when the skill extraction process encounters
    an error, such as spaCy processing failures, invalid text input,
    or issues with the skill catalog or PhraseMatcher.
    
    Attributes:
        message: Human-readable error description
        text_snippet: Optional snippet of the text that caused the error
    """
    
    def __init__(self, message: str, text_snippet: Optional[str] = None) -> None:
        """
        Initialize the skill extraction error.
        
        Args:
            message: Human-readable error description
            text_snippet: Optional snippet of problematic text (truncated for logging)
        """
        self.text_snippet = text_snippet
        
        # Enhance message with text snippet if provided
        if self.text_snippet:
            # Truncate snippet to avoid excessive log messages
            max_length = 100
            truncated = (self.text_snippet[:max_length] + "...") if len(self.text_snippet) > max_length else self.text_snippet
            enhanced_message = f"{message}. Text snippet: '{truncated}'"
        else:
            enhanced_message = message
            
        super().__init__(enhanced_message)


class ScoringError(ResumeScreenerError):
    """
    Raised when scoring computation fails.
    
    This exception is raised when the scoring engine encounters an error
    during candidate score calculation, such as invalid similarity values,
    weight validation failures, or mathematical computation errors.
    
    Attributes:
        message: Human-readable error description
        candidate_id: Optional identifier of the candidate being scored
        score_component: Optional name of the score component that failed
    """
    
    def __init__(
        self, 
        message: str, 
        candidate_id: Optional[str] = None,
        score_component: Optional[str] = None
    ) -> None:
        """
        Initialize the scoring error.
        
        Args:
            message: Human-readable error description
            candidate_id: Optional identifier of the candidate being scored
            score_component: Optional name of the failing score component
                           (e.g., 'similarity_score', 'required_skill_score')
        """
        self.candidate_id = candidate_id
        self.score_component = score_component
        
        # Enhance message with context if provided
        context_parts = []
        if self.candidate_id:
            context_parts.append(f"candidate_id='{self.candidate_id}'")
        if self.score_component:
            context_parts.append(f"component='{self.score_component}'")
            
        if context_parts:
            context_str = ", ".join(context_parts)
            enhanced_message = f"{message} ({context_str})"
        else:
            enhanced_message = message
            
        super().__init__(enhanced_message)
