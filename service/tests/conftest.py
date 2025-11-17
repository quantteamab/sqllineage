"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_sql_simple():
    """Simple SQL query for testing."""
    return "SELECT col1, col2 FROM table1"


@pytest.fixture
def sample_sql_with_join():
    """SQL query with JOIN for testing."""
    return """
        SELECT t1.id, t1.name, t2.value
        FROM schema1.table1 t1
        JOIN schema2.table2 t2 ON t1.id = t2.id
    """


@pytest.fixture
def sample_sql_insert():
    """SQL INSERT query for testing."""
    return """
        INSERT INTO target_table (col1, col2)
        SELECT source_col1, source_col2
        FROM source_table
    """


@pytest.fixture
def sample_sql_cte():
    """SQL query with CTE for testing."""
    return """
        WITH temp_cte AS (
            SELECT id, name FROM source_table
        )
        SELECT id, name FROM temp_cte
    """


@pytest.fixture
def sample_sql_multiple_statements():
    """Multiple SQL statements for testing."""
    return """
        CREATE TABLE temp_table AS SELECT * FROM source1;
        INSERT INTO target SELECT * FROM temp_table;
    """
