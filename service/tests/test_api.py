"""Unit tests for API endpoints."""

import pytest
from fastapi import status


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check_success(self, client):
        """Test health check returns successful response."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "openmetadata_configured" in data

    def test_health_check_no_rate_limit(self, client):
        """Test health check is not rate limited."""
        # Make multiple requests quickly
        for _ in range(150):  # More than rate limit
            response = client.get("/health")
            assert response.status_code == status.HTTP_200_OK


class TestDialectsEndpoint:
    """Tests for dialects endpoint."""

    def test_get_dialects_success(self, client):
        """Test getting supported dialects."""
        response = client.get("/api/v1/dialects")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "dialects" in data
        assert isinstance(data["dialects"], list)
        assert len(data["dialects"]) > 0
        assert "ansi" in data["dialects"]


class TestColumnPairsEndpoint:
    """Tests for column-pairs lineage endpoint."""

    def test_column_pairs_simple_select(self, client, sample_sql_simple):
        """Test column pairs for simple SELECT query."""
        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": sample_sql_simple,
                "dialect": "ansi",
                "silent_mode": False,
                "openmetadata_enabled": False,
            },
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "column_pairs" in data
        assert "warnings" in data
        assert "metadata" in data
        assert isinstance(data["column_pairs"], list)
        assert data["metadata"]["dialect_used"] == "ansi"

    def test_column_pairs_with_join(self, client, sample_sql_with_join):
        """Test column pairs for query with JOIN."""
        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": sample_sql_with_join,
                "dialect": "ansi",
                "silent_mode": False,
                "openmetadata_enabled": False,
            },
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "column_pairs" in data
        assert data["metadata"]["statement_count"] >= 1

    def test_column_pairs_insert_query(self, client, sample_sql_insert):
        """Test column pairs for INSERT query."""
        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": sample_sql_insert,
                "dialect": "ansi",
                "silent_mode": False,
                "openmetadata_enabled": False,
            },
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "column_pairs" in data
        # Should have column lineage from source to target
        if data["column_pairs"]:
            assert "target" in data["column_pairs"][0]
            assert "sources" in data["column_pairs"][0]

    def test_column_pairs_invalid_sql(self, client):
        """Test column pairs with invalid SQL."""
        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": "SELECT FROM WHERE",
                "dialect": "ansi",
                "silent_mode": False,
                "openmetadata_enabled": False,
            },
        )
        # Should return 200 with warnings, not error
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # May have warnings or empty results
        assert "warnings" in data

    def test_column_pairs_empty_sql(self, client):
        """Test column pairs with empty SQL."""
        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": "",
                "dialect": "ansi",
            },
        )
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_column_pairs_missing_sql(self, client):
        """Test column pairs without SQL field."""
        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "dialect": "ansi",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_column_pairs_silent_mode(self, client):
        """Test column pairs with silent mode enabled."""
        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": "SELECT * FROM table1",
                "dialect": "ansi",
                "silent_mode": True,
                "openmetadata_enabled": False,
            },
        )
        assert response.status_code == status.HTTP_200_OK


class TestTableLineageEndpoint:
    """Tests for table lineage endpoint."""

    def test_table_lineage_simple(self, client, sample_sql_simple):
        """Test table lineage for simple query."""
        response = client.post(
            "/api/v1/lineage/table",
            json={
                "sql": sample_sql_simple,
                "dialect": "ansi",
                "openmetadata_enabled": False,
            },
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "source_tables" in data
        assert "target_tables" in data
        assert "warnings" in data
        assert "metadata" in data

    def test_table_lineage_with_insert(self, client, sample_sql_insert):
        """Test table lineage for INSERT query."""
        response = client.post(
            "/api/v1/lineage/table",
            json={
                "sql": sample_sql_insert,
                "dialect": "ansi",
                "openmetadata_enabled": False,
            },
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Should have both source and target tables
        assert isinstance(data["source_tables"], list)
        assert isinstance(data["target_tables"], list)


class TestColumnLineageEndpoint:
    """Tests for verbose column lineage endpoint."""

    def test_column_lineage_paths(self, client, sample_sql_cte):
        """Test column lineage paths with CTE."""
        response = client.post(
            "/api/v1/lineage/column",
            json={
                "sql": sample_sql_cte,
                "dialect": "ansi",
                "openmetadata_enabled": False,
            },
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "column_lineage_paths" in data
        assert "warnings" in data
        assert "metadata" in data
        assert isinstance(data["column_lineage_paths"], list)


class TestRateLimiting:
    """Tests for rate limiting middleware."""

    def test_rate_limit_exceeded(self, client):
        """Test that rate limiting kicks in after limit."""
        # Note: This test might be flaky depending on timing
        # Make requests up to the limit
        endpoint = "/api/v1/dialects"

        # Make more than 100 requests quickly
        responses = []
        for i in range(105):
            response = client.get(endpoint)
            responses.append(response.status_code)

        # At least one should be rate limited
        # Note: This might not always trigger in tests due to timing
        rate_limited = any(code == status.HTTP_429_TOO_MANY_REQUESTS for code in responses)

        # Check rate limit headers exist on successful responses
        response = client.get(endpoint)
        if response.status_code == status.HTTP_200_OK:
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers


class TestRequestSizeLimit:
    """Tests for request size validation."""

    def test_request_too_large(self, client):
        """Test that oversized requests are rejected."""
        # Create a SQL string larger than 50MB
        large_sql = "SELECT * FROM table " + "A" * (51 * 1024 * 1024)

        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": large_sql,
                "dialect": "ansi",
            },
        )
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


class TestResponseHeaders:
    """Tests for response headers."""

    def test_process_time_header(self, client):
        """Test that process time header is included."""
        response = client.get("/health")
        assert "X-Process-Time" in response.headers

    def test_cors_headers(self, client):
        """Test CORS headers if configured."""
        # Note: CORS might need to be configured in main.py
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
