"""
Pytest configuration and shared fixtures for ResumeScreener-AI tests.

This module provides reusable test fixtures for:
- Sample resume data
- Job descriptions
- Role profiles
- Mock data generators
"""

import pytest
import pandas as pd
from pathlib import Path
from typing import Dict, List


@pytest.fixture
def sample_resumes() -> pd.DataFrame:
    """
    Provide sample resume data for testing.
    
    Returns:
        DataFrame with columns: candidate_id, candidate_name, resume_text
    """
    return pd.DataFrame({
        'candidate_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
        'candidate_name': [
            'Alice Johnson',
            'Bob Smith',
            'Carol Williams',
            'David Brown',
            'Eve Davis'
        ],
        'resume_text': [
            # Strong candidate - has most required skills
            """
            Data Scientist with 5 years of experience in Python, machine learning, 
            and statistical analysis. Expert in pandas, scikit-learn, SQL, and data 
            visualization. Built predictive models using regression and classification.
            """,
            # Medium candidate - has some required skills
            """
            Software Engineer with Python experience. Worked with SQL databases and 
            basic data analysis. Familiar with pandas and numpy. Strong problem-solving 
            skills and team collaboration.
            """,
            # Weak candidate - few relevant skills
            """
            Marketing Manager with experience in campaign management and social media. 
            Basic Excel skills and data reporting. Strong communication and leadership 
            abilities.
            """,
            # Strong candidate with important skills
            """
            Senior Data Scientist specializing in machine learning and deep learning. 
            Expert in Python, SQL, statistics, pandas, scikit-learn, TensorFlow, and 
            PyTorch. Experience with NLP, computer vision, and AWS deployment. Docker 
            and Kubernetes proficiency.
            """,
            # Empty resume edge case
            ""
        ]
    })


@pytest.fixture
def sample_job_description() -> str:
    """
    Provide sample job description for testing.
    
    Returns:
        Job description text with required and important skills
    """
    return """
    We are seeking a Data Scientist to join our analytics team.
    
    Required Skills:
    - Python programming
    - Machine learning algorithms
    - Statistical analysis
    - SQL and database management
    - pandas and scikit-learn
    
    Nice to Have:
    - Deep learning frameworks (TensorFlow, PyTorch)
    - Natural language processing
    - Cloud platforms (AWS, GCP, Azure)
    - Docker and containerization
    - Big data tools (Spark, Hadoop)
    
    You will work on building predictive models, analyzing large datasets, 
    and deploying machine learning solutions to production.
    """


@pytest.fixture
def sample_role_profile() -> Dict[str, List[str]]:
    """
    Provide sample role profile configuration.
    
    Returns:
        Dictionary with required_skills and important_skills lists
    """
    return {
        'required_skills': [
            'python',
            'machine learning',
            'statistics',
            'sql',
            'pandas',
            'scikit-learn'
        ],
        'important_skills': [
            'deep learning',
            'nlp',
            'aws',
            'docker',
            'spark'
        ]
    }


@pytest.fixture
def empty_resumes() -> pd.DataFrame:
    """
    Provide empty DataFrame for edge case testing.
    
    Returns:
        Empty DataFrame with correct schema
    """
    return pd.DataFrame({
        'candidate_id': [],
        'candidate_name': [],
        'resume_text': []
    })


@pytest.fixture
def invalid_resumes_missing_column() -> pd.DataFrame:
    """
    Provide DataFrame with missing required column for error testing.
    
    Returns:
        DataFrame missing the resume_text column
    """
    return pd.DataFrame({
        'candidate_id': ['C001', 'C002'],
        'candidate_name': ['Alice', 'Bob']
        # Missing 'resume_text' column
    })


@pytest.fixture
def resumes_with_null_text() -> pd.DataFrame:
    """
    Provide DataFrame with null resume text for edge case testing.
    
    Returns:
        DataFrame with None values in resume_text
    """
    return pd.DataFrame({
        'candidate_id': ['C001', 'C002', 'C003'],
        'candidate_name': ['Alice', 'Bob', 'Carol'],
        'resume_text': [
            'Valid resume text with Python and SQL skills.',
            None,  # Null value
            ''  # Empty string
        ]
    })


@pytest.fixture
def sample_skills() -> Dict[str, List[str]]:
    """
    Provide sample skill sets for testing.
    
    Returns:
        Dictionary with various skill categories
    """
    return {
        'programming': ['python', 'java', 'javascript', 'c++', 'r'],
        'data_science': ['machine learning', 'deep learning', 'statistics', 
                        'data analysis', 'nlp'],
        'tools': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'],
        'databases': ['sql', 'postgresql', 'mongodb', 'mysql', 'redis'],
        'cloud': ['aws', 'gcp', 'azure', 'docker', 'kubernetes']
    }


@pytest.fixture
def temp_test_dir(tmp_path: Path) -> Path:
    """
    Provide temporary directory for file-based tests.
    
    Args:
        tmp_path: pytest's built-in temporary directory fixture
    
    Returns:
        Path to temporary test directory
    """
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return test_dir


@pytest.fixture
def sample_csv_file(temp_test_dir: Path, sample_resumes: pd.DataFrame) -> Path:
    """
    Create a temporary CSV file with sample resume data.
    
    Args:
        temp_test_dir: Temporary directory fixture
        sample_resumes: Sample resume DataFrame fixture
    
    Returns:
        Path to the created CSV file
    """
    csv_path = temp_test_dir / "resumes.csv"
    sample_resumes.to_csv(csv_path, index=False)
    return csv_path


# Pytest configuration
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "property: mark test as a property-based test"
    )
