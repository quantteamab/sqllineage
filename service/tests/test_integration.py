"""Integration tests with real SQL statements."""

import pytest
from fastapi import status


class TestRealWorldQueries:
    """Integration tests with realistic SQL queries."""

    def test_complex_hive_query(self, client):
        """Test complex Hive query with multiple tables and CTEs."""
        sql = """
            WITH user_orders AS (
                SELECT
                    u.user_id,
                    u.username,
                    o.order_id,
                    o.order_date,
                    o.total_amount
                FROM prod.users u
                JOIN prod.orders o ON u.user_id = o.user_id
                WHERE o.order_date >= '2024-01-01'
            ),
            order_summary AS (
                SELECT
                    user_id,
                    username,
                    COUNT(order_id) as order_count,
                    SUM(total_amount) as total_spent
                FROM user_orders
                GROUP BY user_id, username
            )
            INSERT INTO analytics.user_metrics
            SELECT
                user_id,
                username,
                order_count,
                total_spent,
                total_spent / order_count as avg_order_value
            FROM order_summary
            WHERE order_count > 0
        """

        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": sql,
                "dialect": "hive",
                "silent_mode": False,
                "openmetadata_enabled": False,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "column_pairs" in data
        assert "metadata" in data
        assert data["metadata"]["statement_count"] >= 1

        # Should have column lineage
        # Note: exact lineage depends on parser capabilities
        print(f"\nColumn pairs found: {len(data['column_pairs'])}")
        for pair in data["column_pairs"]:
            print(f"  {pair['target']} <- {pair['sources']}")

    def test_spark_sql_query(self, client):
        """Test Spark SQL query with window functions."""
        sql = """
            INSERT INTO warehouse.daily_metrics
            SELECT
                date,
                product_id,
                sales_amount,
                ROW_NUMBER() OVER (PARTITION BY date ORDER BY sales_amount DESC) as sales_rank,
                SUM(sales_amount) OVER (PARTITION BY product_id ORDER BY date
                    ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) as rolling_7day_sales
            FROM staging.raw_sales
            WHERE date BETWEEN '2024-01-01' AND '2024-12-31'
        """

        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": sql,
                "dialect": "sparksql",
                "silent_mode": False,
                "openmetadata_enabled": False,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "column_pairs" in data
        print(f"\nSpark SQL column pairs: {len(data['column_pairs'])}")

    def test_postgres_materialized_view(self, client):
        """Test PostgreSQL materialized view creation."""
        sql = """
            CREATE MATERIALIZED VIEW analytics.customer_summary AS
            SELECT
                c.customer_id,
                c.customer_name,
                c.email,
                COUNT(DISTINCT o.order_id) as total_orders,
                SUM(oi.quantity * oi.unit_price) as lifetime_value,
                MAX(o.order_date) as last_order_date
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_id, c.customer_name, c.email
        """

        response = client.post(
            "/api/v1/lineage/table",
            json={
                "sql": sql,
                "dialect": "postgres",
                "silent_mode": False,
                "openmetadata_enabled": False,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        print(f"\nSource tables: {data['source_tables']}")
        print(f"Target tables: {data['target_tables']}")

        # Should have multiple source tables
        assert len(data["source_tables"]) >= 2

    def test_multiple_insert_statements(self, client, sample_sql_multiple_statements):
        """Test multiple SQL statements separated by semicolons."""
        response = client.post(
            "/api/v1/lineage/table",
            json={
                "sql": sample_sql_multiple_statements,
                "dialect": "ansi",
                "silent_mode": False,
                "openmetadata_enabled": False,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should process multiple statements
        assert data["metadata"]["statement_count"] >= 2
        print(f"\nProcessed {data['metadata']['statement_count']} statements")

    def test_bigquery_nested_query(self, client):
        """Test BigQuery query with nested fields."""
        sql = """
            SELECT
                user_id,
                event_timestamp,
                event_params.key as param_key,
                event_params.value.string_value as param_value
            FROM `project.dataset.events`
            CROSS JOIN UNNEST(event_params) as event_params
            WHERE DATE(event_timestamp) = CURRENT_DATE()
        """

        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": sql,
                "dialect": "bigquery",
                "silent_mode": True,  # Use silent mode for potentially unsupported syntax
                "openmetadata_enabled": False,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check for warnings if syntax not fully supported
        if data["warnings"]:
            print(f"\nWarnings: {data['warnings']}")

    def test_tsql_merge_statement(self, client):
        """Test T-SQL MERGE statement."""
        sql = """
            MERGE INTO target_table AS target
            USING source_table AS source
            ON target.id = source.id
            WHEN MATCHED THEN
                UPDATE SET
                    target.value = source.value,
                    target.updated_date = source.updated_date
            WHEN NOT MATCHED THEN
                INSERT (id, value, updated_date)
                VALUES (source.id, source.value, source.updated_date);
        """

        response = client.post(
            "/api/v1/lineage/table",
            json={
                "sql": sql,
                "dialect": "tsql",
                "silent_mode": True,
                "openmetadata_enabled": False,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        print(f"\nMERGE statement lineage: {data}")


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_very_long_query(self, client):
        """Test handling of very long SQL query (but within limits)."""
        # Create a query with many columns
        columns = ", ".join([f"col{i}" for i in range(1000)])
        sql = f"SELECT {columns} FROM large_table"

        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": sql,
                "dialect": "ansi",
                "silent_mode": False,
                "openmetadata_enabled": False,
            },
        )

        assert response.status_code == status.HTTP_200_OK

    def test_query_with_comments(self, client):
        """Test SQL query with comments."""
        sql = """
            -- This is a comment
            /* Multi-line
               comment */
            SELECT
                col1,  -- inline comment
                col2
            FROM table1
            WHERE col1 > 0
        """

        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": sql,
                "dialect": "ansi",
                "openmetadata_enabled": False,
            },
        )

        assert response.status_code == status.HTTP_200_OK

    def test_query_with_special_characters(self, client):
        """Test SQL query with special characters in identifiers."""
        sql = """
            SELECT
                `special-column`,
                "quoted column",
                [bracketed_column]
            FROM `special-table`
        """

        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": sql,
                "dialect": "bigquery",
                "silent_mode": True,
                "openmetadata_enabled": False,
            },
        )

        assert response.status_code == status.HTTP_200_OK

    def test_silent_mode_with_errors(self, client):
        """Test that silent mode handles errors gracefully."""
        sql = """
            SELECT * FROM table1;
            THIS IS INVALID SQL;
            SELECT * FROM table2;
        """

        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": sql,
                "dialect": "ansi",
                "silent_mode": True,
                "openmetadata_enabled": False,
            },
        )

        # Should still return 200 with partial results
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # May have warnings
        if data["warnings"]:
            print(f"\nSilent mode warnings: {data['warnings']}")


class TestPerformance:
    """Performance and stress tests."""

    def test_processing_time_recorded(self, client):
        """Test that processing time is recorded in metadata."""
        sql = "SELECT col1, col2 FROM table1 JOIN table2 ON table1.id = table2.id"

        response = client.post(
            "/api/v1/lineage/column-pairs",
            json={
                "sql": sql,
                "dialect": "ansi",
                "openmetadata_enabled": False,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "metadata" in data
        assert "processing_time_ms" in data["metadata"]
        assert data["metadata"]["processing_time_ms"] > 0

        print(f"\nProcessing time: {data['metadata']['processing_time_ms']:.2f}ms")

    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import concurrent.futures

        sql = "SELECT * FROM table1"

        def make_request():
            return client.post(
                "/api/v1/lineage/column-pairs",
                json={
                    "sql": sql,
                    "dialect": "ansi",
                    "openmetadata_enabled": False,
                },
            )

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(r.status_code == status.HTTP_200_OK for r in results)
        print(f"\nAll {len(results)} concurrent requests succeeded")


class TestDialectSpecific:
    """Tests for dialect-specific SQL features."""

    @pytest.mark.parametrize("dialect,sql", [
        ("hive", "SELECT * FROM table1 LATERAL VIEW EXPLODE(array_col) t AS element"),
        ("sparksql", "SELECT * FROM table1 WHERE date = current_date()"),
        ("postgres", "SELECT * FROM table1 WHERE col1 IS DISTINCT FROM col2"),
        ("tsql", "SELECT TOP 10 * FROM table1"),
        ("mysql", "SELECT * FROM table1 LIMIT 10"),
        ("oracle", "SELECT * FROM table1 FETCH FIRST 10 ROWS ONLY"),
    ])
    def test_dialect_specific_syntax(self, client, dialect, sql):
        """Test various dialect-specific SQL syntax."""
        response = client.post(
            "/api/v1/lineage/table",
            json={
                "sql": sql,
                "dialect": dialect,
                "silent_mode": True,
                "openmetadata_enabled": False,
            },
        )

        # Should return 200 (may have warnings for unsupported features)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        print(f"\n{dialect}: {data['metadata']['successful_statements']} successful")
