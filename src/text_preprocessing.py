"""
Text normalization and preprocessing helpers for ResumeScreener-AI.

This module provides production-grade text preprocessing functions for
resume and job description text, including cleaning, tokenization,
stopword removal, and stemming. All functions include comprehensive
error handling, input validation, and logging.

Example:
    Basic text preprocessing for TF-IDF vectorization:
    
    >>> from text_preprocessing import preprocess_for_vectorizer
    >>> text = "Python Developer with 5+ years of experience in ML"
    >>> processed = preprocess_for_vectorizer(text)
    >>> print(processed)
    'python developer 5+ years experience ml'
    
    Advanced preprocessing with stemming:
    
    >>> processed = preprocess_for_vectorizer(text, use_stemming=True)
    >>> print(processed)
    'python develop 5+ year experi ml'
"""

import re
from typing import Iterable, List

from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from .logging_config import get_logger

# Module-level logger
logger = get_logger(__name__)

# Initialize preprocessing components
TOKENIZER = RegexpTokenizer(r"[A-Za-z][A-Za-z0-9\+\#\-\.]*")
STEMMER = SnowballStemmer("english")
STOPWORDS = set(ENGLISH_STOP_WORDS)

logger.debug(
    f"Text preprocessing module initialized: "
    f"tokenizer={TOKENIZER.pattern}, "
    f"stemmer=SnowballStemmer(english), "
    f"stopwords_count={len(STOPWORDS)}"
)


def normalize_whitespace(text: str) -> str:
    """
    Collapse repeated whitespace and strip outer spaces.
    
    This function normalizes whitespace by replacing any sequence of
    whitespace characters (spaces, tabs, newlines) with a single space
    and removing leading/trailing whitespace.
    
    Args:
        text: Input text string to normalize. Can be empty.
    
    Returns:
        Normalized text with single spaces and no leading/trailing whitespace.
        Returns empty string if input is empty.
    
    Raises:
        TypeError: If text is not a string
        
    Example:
        >>> normalize_whitespace("Hello    world\\n\\ntest")
        'Hello world test'
        >>> normalize_whitespace("  spaces  ")
        'spaces'
        >>> normalize_whitespace("")
        ''
    """
    # Input validation
    if not isinstance(text, str):
        logger.error(f"Invalid input type for normalize_whitespace: {type(text)}")
        raise TypeError(f"text must be a string, got {type(text).__name__}")
    
    # Handle empty text gracefully
    if not text:
        logger.debug("normalize_whitespace: empty text provided, returning empty string")
        return ""
    
    try:
        logger.debug(f"Normalizing whitespace for text of length {len(text)}")
        result = re.sub(r"\s+", " ", text).strip()
        logger.debug(f"Whitespace normalized: {len(text)} -> {len(result)} characters")
        return result
    except Exception as e:
        logger.error(f"Error normalizing whitespace: {e}", exc_info=True)
        raise


def clean_text(text: str) -> str:
    """
    Lowercase and remove non-ASCII symbols that are not useful for matching.
    
    This function performs text cleaning by converting to lowercase and
    removing special characters while preserving alphanumeric characters
    and technical symbols commonly found in resumes (e.g., +, #, -, ., /).
    
    Args:
        text: Input text string to clean. Can be empty.
    
    Returns:
        Cleaned and lowercased text with normalized whitespace.
        Returns empty string if input is empty.
    
    Raises:
        TypeError: If text is not a string
        
    Example:
        >>> clean_text("Python Developer @ Company!")
        'python developer company'
        >>> clean_text("C++ and C# Developer")
        'c++ and c# developer'
        >>> clean_text("")
        ''
    """
    # Input validation
    if not isinstance(text, str):
        logger.error(f"Invalid input type for clean_text: {type(text)}")
        raise TypeError(f"text must be a string, got {type(text).__name__}")
    
    # Handle empty text gracefully
    if not text:
        logger.debug("clean_text: empty text provided, returning empty string")
        return ""
    
    try:
        logger.debug(f"Cleaning text of length {len(text)}")
        lowered = text.lower()
        normalized = re.sub(r"[^a-z0-9\s\+\#\-\.\/]", " ", lowered)
        result = normalize_whitespace(normalized)
        logger.debug(f"Text cleaned: {len(text)} -> {len(result)} characters")
        return result
    except Exception as e:
        logger.error(f"Error cleaning text: {e}", exc_info=True)
        raise


def tokenize(text: str) -> List[str]:
    """
    Tokenize text while preserving terms like c++ or scikit-learn.
    
    This function uses a specialized tokenizer that preserves technical
    terms commonly found in resumes and job descriptions, including
    programming languages (C++, C#), frameworks (scikit-learn), and
    version numbers (Python3.9).
    
    Args:
        text: Input text string to tokenize. Can be empty.
    
    Returns:
        List of tokens extracted from the text. Returns empty list if
        input is empty or contains no valid tokens.
    
    Raises:
        TypeError: If text is not a string
        
    Example:
        >>> tokenize("Python C++ scikit-learn")
        ['Python', 'C++', 'scikit-learn']
        >>> tokenize("Experience with ML/AI")
        ['Experience', 'with', 'ML', 'AI']
        >>> tokenize("")
        []
    """
    # Input validation
    if not isinstance(text, str):
        logger.error(f"Invalid input type for tokenize: {type(text)}")
        raise TypeError(f"text must be a string, got {type(text).__name__}")
    
    # Handle empty text gracefully
    if not text:
        logger.debug("tokenize: empty text provided, returning empty list")
        return []
    
    try:
        logger.debug(f"Tokenizing text of length {len(text)}")
        tokens = TOKENIZER.tokenize(text)
        logger.debug(f"Tokenization complete: extracted {len(tokens)} tokens")
        return tokens
    except Exception as e:
        logger.error(f"Error tokenizing text: {e}", exc_info=True)
        raise


def remove_stopwords(tokens: Iterable[str]) -> List[str]:
    """
    Remove common stop words and very short tokens.
    
    This function filters out common English stop words (e.g., 'the', 'is', 'at')
    and single-character tokens that typically don't contribute to semantic
    meaning in resume screening.
    
    Args:
        tokens: Iterable of token strings to filter. Can be empty.
    
    Returns:
        List of tokens with stop words removed. Returns empty list if
        input is empty or all tokens are stop words.
    
    Raises:
        TypeError: If tokens is not iterable or contains non-string elements
        
    Example:
        >>> remove_stopwords(['python', 'is', 'a', 'programming', 'language'])
        ['python', 'programming', 'language']
        >>> remove_stopwords(['the', 'and', 'or'])
        []
        >>> remove_stopwords([])
        []
    """
    # Input validation
    try:
        tokens_list = list(tokens)
    except TypeError as e:
        logger.error(f"Invalid input type for remove_stopwords: {type(tokens)}")
        raise TypeError(f"tokens must be iterable, got {type(tokens).__name__}") from e
    
    # Validate all elements are strings
    for i, token in enumerate(tokens_list):
        if not isinstance(token, str):
            logger.error(f"Invalid token type at index {i}: {type(token)}")
            raise TypeError(f"All tokens must be strings, got {type(token).__name__} at index {i}")
    
    # Handle empty tokens gracefully
    if not tokens_list:
        logger.debug("remove_stopwords: empty token list provided, returning empty list")
        return []
    
    try:
        logger.debug(f"Removing stopwords from {len(tokens_list)} tokens")
        filtered = [token for token in tokens_list if token not in STOPWORDS and len(token) > 1]
        logger.debug(f"Stopword removal complete: {len(tokens_list)} -> {len(filtered)} tokens")
        return filtered
    except Exception as e:
        logger.error(f"Error removing stopwords: {e}", exc_info=True)
        raise


def stem_tokens(tokens: Iterable[str]) -> List[str]:
    """
    Apply stemming for robust lexical comparison.
    
    This function applies Snowball stemming to reduce words to their
    root form, enabling better matching between different word forms
    (e.g., 'developing', 'developer', 'develops' -> 'develop').
    
    Args:
        tokens: Iterable of token strings to stem. Can be empty.
    
    Returns:
        List of stemmed tokens. Returns empty list if input is empty.
    
    Raises:
        TypeError: If tokens is not iterable or contains non-string elements
        
    Example:
        >>> stem_tokens(['developing', 'developer', 'develops'])
        ['develop', 'develop', 'develop']
        >>> stem_tokens(['python', 'programming'])
        ['python', 'program']
        >>> stem_tokens([])
        []
    """
    # Input validation
    try:
        tokens_list = list(tokens)
    except TypeError as e:
        logger.error(f"Invalid input type for stem_tokens: {type(tokens)}")
        raise TypeError(f"tokens must be iterable, got {type(tokens).__name__}") from e
    
    # Validate all elements are strings
    for i, token in enumerate(tokens_list):
        if not isinstance(token, str):
            logger.error(f"Invalid token type at index {i}: {type(token)}")
            raise TypeError(f"All tokens must be strings, got {type(token).__name__} at index {i}")
    
    # Handle empty tokens gracefully
    if not tokens_list:
        logger.debug("stem_tokens: empty token list provided, returning empty list")
        return []
    
    try:
        logger.debug(f"Stemming {len(tokens_list)} tokens")
        stemmed = [STEMMER.stem(token) for token in tokens_list]
        logger.debug(f"Stemming complete: processed {len(stemmed)} tokens")
        return stemmed
    except Exception as e:
        logger.error(f"Error stemming tokens: {e}", exc_info=True)
        raise


def preprocess_for_vectorizer(text: str, use_stemming: bool = False) -> str:
    """
    Convert raw text into normalized text suitable for TF-IDF vectorization.
    
    This is the main preprocessing pipeline that combines cleaning, tokenization,
    stopword removal, and optional stemming to prepare text for TF-IDF
    vectorization in the resume screening pipeline.
    
    The preprocessing steps are:
    1. Clean text (lowercase, remove special characters)
    2. Tokenize (preserve technical terms like C++, scikit-learn)
    3. Remove stopwords and short tokens
    4. Apply stemming (optional)
    5. Join tokens into space-separated string
    
    Args:
        text: Raw input text (resume, job description, etc.). Can be empty.
        use_stemming: Whether to apply stemming to tokens. Default is False.
                     Set to True for more aggressive normalization.
    
    Returns:
        Preprocessed text string ready for TF-IDF vectorization.
        Returns empty string if input is empty or contains no valid tokens.
    
    Raises:
        TypeError: If text is not a string or use_stemming is not a boolean
        
    Example:
        >>> text = "Python Developer with 5+ years of experience in ML"
        >>> preprocess_for_vectorizer(text)
        'python developer 5+ years experience ml'
        
        >>> preprocess_for_vectorizer(text, use_stemming=True)
        'python develop 5+ year experi ml'
        
        >>> preprocess_for_vectorizer("")
        ''
    
    Note:
        This function is designed for TF-IDF vectorization. For skill extraction,
        use the raw or lightly cleaned text to preserve exact skill names.
    """
    # Input validation
    if not isinstance(text, str):
        logger.error(f"Invalid input type for preprocess_for_vectorizer: {type(text)}")
        raise TypeError(f"text must be a string, got {type(text).__name__}")
    
    if not isinstance(use_stemming, bool):
        logger.error(f"Invalid use_stemming type: {type(use_stemming)}")
        raise TypeError(f"use_stemming must be a boolean, got {type(use_stemming).__name__}")
    
    # Handle empty text gracefully
    if not text:
        logger.debug("preprocess_for_vectorizer: empty text provided, returning empty string")
        return ""
    
    try:
        logger.info(
            f"Starting text preprocessing: length={len(text)}, "
            f"use_stemming={use_stemming}"
        )
        
        # Step 1: Clean text
        cleaned = clean_text(text)
        if not cleaned:
            logger.warning("Text cleaning resulted in empty string")
            return ""
        
        # Step 2: Tokenize
        tokens = tokenize(cleaned)
        if not tokens:
            logger.warning("Tokenization resulted in no tokens")
            return ""
        
        # Step 3: Remove stopwords
        filtered_tokens = remove_stopwords(tokens)
        if not filtered_tokens:
            logger.warning("Stopword removal resulted in no tokens")
            return ""
        
        # Step 4: Apply stemming if requested
        if use_stemming:
            filtered_tokens = stem_tokens(filtered_tokens)
            if not filtered_tokens:
                logger.warning("Stemming resulted in no tokens")
                return ""
        
        # Step 5: Join tokens
        result = " ".join(filtered_tokens)
        
        logger.info(
            f"Text preprocessing complete: "
            f"input_length={len(text)}, "
            f"output_length={len(result)}, "
            f"tokens={len(filtered_tokens)}"
        )
        
        return result
        
    except Exception as e:
        logger.error(
            f"Error preprocessing text: {e}. "
            f"Text length: {len(text)}, use_stemming: {use_stemming}",
            exc_info=True
        )
        raise

