"""Pydantic models for request and response validation."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class LineageRequest(BaseModel):
    """Request model for lineage analysis."""

    sql: str = Field(
        ...,
        description="SQL query text to analyze. Multiple statements can be separated by semicolons.",
        min_length=1,
    )
    dialect: str = Field(
        default="ansi",
        description="SQL dialect to use for parsing (e.g., ansi, hive, sparksql, tsql)",
    )
    silent_mode: bool = Field(
        default=False,
        description="If True, skip unsupported statements without errors",
    )
    openmetadata_enabled: bool = Field(
        default=True,
        description="If True, use OpenMetadata for schema metadata resolution",
    )

    @field_validator("sql")
    @classmethod
    def validate_sql_not_empty(cls, v: str) -> str:
        """Validate that SQL is not just whitespace."""
        if not v.strip():
            raise ValueError("SQL cannot be empty or just whitespace")
        return v


class ColumnPair(BaseModel):
    """Represents a single column lineage pair."""

    target: str = Field(
        ...,
        description="Target column in format: schema.table.column or table.column",
    )
    sources: List[str] = Field(
        ...,
        description="List of source columns in format: schema.table.column or table.column",
    )


class LineageMetadata(BaseModel):
    """Metadata about the lineage analysis."""

    processing_time_ms: float = Field(
        ...,
        description="Time taken to process the request in milliseconds",
    )
    dialect_used: str = Field(..., description="SQL dialect used for parsing")
    statement_count: int = Field(..., description="Total number of SQL statements")
    successful_statements: int = Field(
        ..., description="Number of successfully parsed statements"
    )
    failed_statements: int = Field(..., description="Number of failed statements")


class ColumnPairsResponse(BaseModel):
    """Response model for column-pairs lineage endpoint."""

    column_pairs: List[ColumnPair] = Field(
        default_factory=list,
        description="List of column lineage pairs",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warnings or errors encountered during processing",
    )
    metadata: LineageMetadata = Field(..., description="Metadata about the analysis")


class TableLineageItem(BaseModel):
    """Represents a table in lineage."""

    schema: Optional[str] = Field(None, description="Schema name")
    table: str = Field(..., description="Table name")


class TableLineageResponse(BaseModel):
    """Response model for table-level lineage endpoint."""

    source_tables: List[TableLineageItem] = Field(
        default_factory=list,
        description="List of source tables",
    )
    target_tables: List[TableLineageItem] = Field(
        default_factory=list,
        description="List of target tables",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warnings or errors encountered during processing",
    )
    metadata: LineageMetadata = Field(..., description="Metadata about the analysis")


class ColumnLineagePath(BaseModel):
    """Represents a full column lineage path."""

    path: List[str] = Field(
        ...,
        description="Full lineage path from source to target",
    )


class ColumnLineageResponse(BaseModel):
    """Response model for verbose column lineage endpoint."""

    column_lineage_paths: List[ColumnLineagePath] = Field(
        default_factory=list,
        description="List of column lineage paths",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warnings or errors encountered during processing",
    )
    metadata: LineageMetadata = Field(..., description="Metadata about the analysis")


class DialectsResponse(BaseModel):
    """Response model for supported dialects endpoint."""

    dialects: List[str] = Field(..., description="List of supported SQL dialects")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    openmetadata_configured: bool = Field(
        ..., description="Whether OpenMetadata is configured"
    )
