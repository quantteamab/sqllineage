"""Lineage analysis router."""

import logging
from typing import List

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import (
    ColumnLineageResponse,
    ColumnPairsResponse,
    DialectsResponse,
    LineageRequest,
    TableLineageResponse,
)
from app.services.lineage_service import LineageService
from app.services.openmetadata_provider import OpenMetadataProvider
from sqllineage.core.metadata.dummy import DummyMetaDataProvider
from sqllineage.runner import LineageRunner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["lineage"])


def _get_metadata_provider(request: LineageRequest):
    """
    Get appropriate metadata provider based on request and configuration.

    :param request: Lineage request
    :return: Metadata provider instance
    """
    if request.openmetadata_enabled and settings.openmetadata_configured:
        try:
            return OpenMetadataProvider(
                base_url=settings.openmetadata_url,
                api_key=settings.openmetadata_api_key,
                timeout=settings.openmetadata_timeout,
                cache_ttl=settings.openmetadata_cache_ttl,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenMetadata provider: {e}")
            return DummyMetaDataProvider()
    return DummyMetaDataProvider()


@router.post("/lineage/column-pairs", response_model=ColumnPairsResponse)
async def analyze_column_pairs(request: LineageRequest) -> ColumnPairsResponse:
    """
    Analyze SQL and return column-level lineage as pairs.

    This endpoint processes SQL statements and returns column lineage
    in the format: target <- sources.

    Args:
        request: Lineage request with SQL and options

    Returns:
        Column pairs with source-target relationships

    Example:
        ```json
        {
          "sql": "INSERT INTO target_table SELECT col1, col2 FROM source_table",
          "dialect": "ansi",
          "silent_mode": false,
          "openmetadata_enabled": true
        }
        ```
    """
    # Validate request size
    sql_size_mb = len(request.sql.encode("utf-8")) / (1024 * 1024)
    if sql_size_mb > settings.max_request_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"SQL size ({sql_size_mb:.2f}MB) exceeds maximum allowed size ({settings.max_request_size_mb}MB)",
        )

    metadata_provider = _get_metadata_provider(request)

    service = LineageService(
        sql=request.sql,
        dialect=request.dialect,
        silent_mode=request.silent_mode,
        metadata_provider=metadata_provider,
    )

    return service.get_column_pairs()


@router.post("/lineage/table", response_model=TableLineageResponse)
async def analyze_table_lineage(request: LineageRequest) -> TableLineageResponse:
    """
    Analyze SQL and return table-level lineage.

    This endpoint processes SQL statements and returns source and target tables.

    Args:
        request: Lineage request with SQL and options

    Returns:
        Table lineage with source and target tables

    Example:
        ```json
        {
          "sql": "INSERT INTO db1.target SELECT * FROM db2.source1 JOIN db2.source2",
          "dialect": "ansi"
        }
        ```
    """
    # Validate request size
    sql_size_mb = len(request.sql.encode("utf-8")) / (1024 * 1024)
    if sql_size_mb > settings.max_request_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"SQL size ({sql_size_mb:.2f}MB) exceeds maximum allowed size ({settings.max_request_size_mb}MB)",
        )

    metadata_provider = _get_metadata_provider(request)

    service = LineageService(
        sql=request.sql,
        dialect=request.dialect,
        silent_mode=request.silent_mode,
        metadata_provider=metadata_provider,
    )

    return service.get_table_lineage()


@router.post("/lineage/column", response_model=ColumnLineageResponse)
async def analyze_column_lineage(request: LineageRequest) -> ColumnLineageResponse:
    """
    Analyze SQL and return verbose column-level lineage with full paths.

    This endpoint processes SQL statements and returns full column lineage paths
    from source to target through any intermediate transformations.

    Args:
        request: Lineage request with SQL and options

    Returns:
        Column lineage paths showing full transformation chains

    Example:
        ```json
        {
          "sql": "CREATE VIEW v AS SELECT col1 FROM t1; SELECT col1 FROM v;",
          "dialect": "ansi"
        }
        ```
    """
    # Validate request size
    sql_size_mb = len(request.sql.encode("utf-8")) / (1024 * 1024)
    if sql_size_mb > settings.max_request_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"SQL size ({sql_size_mb:.2f}MB) exceeds maximum allowed size ({settings.max_request_size_mb}MB)",
        )

    metadata_provider = _get_metadata_provider(request)

    service = LineageService(
        sql=request.sql,
        dialect=request.dialect,
        silent_mode=request.silent_mode,
        metadata_provider=metadata_provider,
    )

    return service.get_column_lineage()


@router.get("/dialects", response_model=DialectsResponse)
async def get_supported_dialects() -> DialectsResponse:
    """
    Get list of supported SQL dialects.

    Returns:
        List of supported SQL dialects

    Example response:
        ```json
        {
          "dialects": ["ansi", "athena", "bigquery", "databricks", "hive", ...]
        }
        ```
    """
    dialects: List[str] = []
    for _, supported_dialects in LineageRunner.supported_dialects().items():
        dialects += supported_dialects

    # Remove duplicates and sort
    dialects = sorted(set(dialects))

    return DialectsResponse(dialects=dialects)
