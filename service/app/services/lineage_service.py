"""Lineage service wrapper for LineageRunner."""

import logging
import time
from collections import defaultdict
from typing import List, Tuple

from sqllineage.core.metadata.dummy import DummyMetaDataProvider
from sqllineage.core.models import Column, SubQuery, Table
from sqllineage.runner import LineageRunner

from app.models import (
    ColumnLineagePath,
    ColumnLineageResponse,
    ColumnPair,
    ColumnPairsResponse,
    LineageMetadata,
    TableLineageItem,
    TableLineageResponse,
)

logger = logging.getLogger(__name__)


class LineageService:
    """
    Service class for SQL lineage analysis.

    This wraps LineageRunner and provides methods to generate
    different types of lineage responses.
    """

    def __init__(
        self,
        sql: str,
        dialect: str = "ansi",
        silent_mode: bool = False,
        metadata_provider=None,
    ):
        """
        Initialize lineage service.

        :param sql: SQL query text
        :param dialect: SQL dialect
        :param silent_mode: Skip unsupported statements
        :param metadata_provider: Metadata provider instance
        """
        self.sql = sql
        self.dialect = dialect
        self.silent_mode = silent_mode
        self.metadata_provider = metadata_provider or DummyMetaDataProvider()
        self.warnings: List[str] = []
        self.statement_count = 0
        self.successful_statements = 0
        self.failed_statements = 0

    def get_column_pairs(self) -> ColumnPairsResponse:
        """
        Get column-level lineage as pairs.

        :return: ColumnPairsResponse with column pairs and metadata
        """
        start_time = time.time()

        try:
            runner = self._create_runner()
            column_pairs = self._extract_column_pairs(runner)

            processing_time_ms = (time.time() - start_time) * 1000

            return ColumnPairsResponse(
                column_pairs=column_pairs,
                warnings=self.warnings,
                metadata=LineageMetadata(
                    processing_time_ms=processing_time_ms,
                    dialect_used=self.dialect,
                    statement_count=self.statement_count,
                    successful_statements=self.successful_statements,
                    failed_statements=self.failed_statements,
                ),
            )
        except Exception as e:
            logger.exception("Error processing column pairs lineage")
            self.warnings.append(f"Error processing lineage: {str(e)}")
            processing_time_ms = (time.time() - start_time) * 1000

            return ColumnPairsResponse(
                column_pairs=[],
                warnings=self.warnings,
                metadata=LineageMetadata(
                    processing_time_ms=processing_time_ms,
                    dialect_used=self.dialect,
                    statement_count=self.statement_count,
                    successful_statements=0,
                    failed_statements=self.statement_count,
                ),
            )

    def get_table_lineage(self) -> TableLineageResponse:
        """
        Get table-level lineage.

        :return: TableLineageResponse with source and target tables
        """
        start_time = time.time()

        try:
            runner = self._create_runner()
            source_tables, target_tables = self._extract_table_lineage(runner)

            processing_time_ms = (time.time() - start_time) * 1000

            return TableLineageResponse(
                source_tables=source_tables,
                target_tables=target_tables,
                warnings=self.warnings,
                metadata=LineageMetadata(
                    processing_time_ms=processing_time_ms,
                    dialect_used=self.dialect,
                    statement_count=self.statement_count,
                    successful_statements=self.successful_statements,
                    failed_statements=self.failed_statements,
                ),
            )
        except Exception as e:
            logger.exception("Error processing table lineage")
            self.warnings.append(f"Error processing lineage: {str(e)}")
            processing_time_ms = (time.time() - start_time) * 1000

            return TableLineageResponse(
                source_tables=[],
                target_tables=[],
                warnings=self.warnings,
                metadata=LineageMetadata(
                    processing_time_ms=processing_time_ms,
                    dialect_used=self.dialect,
                    statement_count=self.statement_count,
                    successful_statements=0,
                    failed_statements=self.statement_count,
                ),
            )

    def get_column_lineage(self) -> ColumnLineageResponse:
        """
        Get verbose column-level lineage with full paths.

        :return: ColumnLineageResponse with lineage paths
        """
        start_time = time.time()

        try:
            runner = self._create_runner()
            lineage_paths = self._extract_column_lineage_paths(runner)

            processing_time_ms = (time.time() - start_time) * 1000

            return ColumnLineageResponse(
                column_lineage_paths=lineage_paths,
                warnings=self.warnings,
                metadata=LineageMetadata(
                    processing_time_ms=processing_time_ms,
                    dialect_used=self.dialect,
                    statement_count=self.statement_count,
                    successful_statements=self.successful_statements,
                    failed_statements=self.failed_statements,
                ),
            )
        except Exception as e:
            logger.exception("Error processing column lineage")
            self.warnings.append(f"Error processing lineage: {str(e)}")
            processing_time_ms = (time.time() - start_time) * 1000

            return ColumnLineageResponse(
                column_lineage_paths=[],
                warnings=self.warnings,
                metadata=LineageMetadata(
                    processing_time_ms=processing_time_ms,
                    dialect_used=self.dialect,
                    statement_count=self.statement_count,
                    successful_statements=0,
                    failed_statements=self.statement_count,
                ),
            )

    def _create_runner(self) -> LineageRunner:
        """
        Create and configure LineageRunner.

        :return: Configured LineageRunner instance
        """
        # Count statements (rough estimate by splitting on semicolons)
        statements = [s.strip() for s in self.sql.split(";") if s.strip()]
        self.statement_count = len(statements)

        try:
            runner = LineageRunner(
                self.sql,
                dialect=self.dialect,
                metadata_provider=self.metadata_provider,
                silent_mode=self.silent_mode,
            )

            # Track successful/failed statements
            # This is a simplified approach - ideally we'd inspect runner internals
            self.successful_statements = self.statement_count
            self.failed_statements = 0

            return runner
        except Exception as e:
            logger.warning(f"Error creating LineageRunner: {e}")
            self.warnings.append(f"Parsing error: {str(e)}")
            self.failed_statements = self.statement_count
            self.successful_statements = 0
            raise

    def _extract_column_pairs(self, runner: LineageRunner) -> List[ColumnPair]:
        """
        Extract column pairs from LineageRunner.

        This replicates the logic from runner.print_column_pairs()
        but returns structured data instead of printing.

        :param runner: LineageRunner instance
        :return: List of ColumnPair objects
        """

        def format_column(col: Column) -> str:
            """Format column as schema.table.column or table.column"""
            parent = col.parent
            if parent is None:
                return col.raw_name
            elif isinstance(parent, Table):
                # For tables: schema.table.column (skip schema if it's <default>)
                if parent.schema and parent.schema.raw_name != "<default>":
                    return f"{parent.schema.raw_name}.{parent.raw_name}.{col.raw_name}"
                else:
                    return f"{parent.raw_name}.{col.raw_name}"
            elif isinstance(parent, SubQuery):
                # For CTEs/subqueries: use alias as "schema"
                return f"{parent.alias}.{col.raw_name}"
            else:
                # For Path or other types
                return f"{parent}.{col.raw_name}"

        # Group sources by target
        lineage_map = defaultdict(list)

        try:
            for path in runner.get_column_lineage():
                if len(path) >= 2:
                    # Use the immediate predecessor as source
                    source, target = path[-2], path[-1]
                else:
                    # Fallback for single-element paths
                    source, target = path[0], path[-1]
                lineage_map[target].append(source)
        except Exception as e:
            logger.warning(f"Error extracting column lineage: {e}")
            self.warnings.append(f"Column lineage extraction warning: {str(e)}")

        # Convert to ColumnPair objects, sorted by target
        column_pairs = []
        for target in sorted(lineage_map.keys(), key=lambda x: format_column(x)):
            sources = lineage_map[target]
            target_str = format_column(target)
            source_strs = [format_column(s) for s in sources]

            column_pairs.append(
                ColumnPair(target=target_str, sources=source_strs)
            )

        return column_pairs

    def _extract_table_lineage(
        self, runner: LineageRunner
    ) -> Tuple[List[TableLineageItem], List[TableLineageItem]]:
        """
        Extract table lineage from LineageRunner.

        :param runner: LineageRunner instance
        :return: Tuple of (source_tables, target_tables)
        """
        try:
            source_tables = [
                TableLineageItem(
                    schema=str(table.schema.raw_name)
                    if table.schema and table.schema.raw_name != "<default>"
                    else None,
                    table=table.raw_name,
                )
                for table in runner.source_tables
            ]

            target_tables = [
                TableLineageItem(
                    schema=str(table.schema.raw_name)
                    if table.schema and table.schema.raw_name != "<default>"
                    else None,
                    table=table.raw_name,
                )
                for table in runner.target_tables
            ]

            return source_tables, target_tables
        except Exception as e:
            logger.warning(f"Error extracting table lineage: {e}")
            self.warnings.append(f"Table lineage extraction warning: {str(e)}")
            return [], []

    def _extract_column_lineage_paths(
        self, runner: LineageRunner
    ) -> List[ColumnLineagePath]:
        """
        Extract full column lineage paths from LineageRunner.

        :param runner: LineageRunner instance
        :return: List of ColumnLineagePath objects
        """

        def format_column(col: Column) -> str:
            """Format column as schema.table.column or table.column"""
            parent = col.parent
            if parent is None:
                return col.raw_name
            elif isinstance(parent, Table):
                if parent.schema and parent.schema.raw_name != "<default>":
                    return f"{parent.schema.raw_name}.{parent.raw_name}.{col.raw_name}"
                else:
                    return f"{parent.raw_name}.{col.raw_name}"
            elif isinstance(parent, SubQuery):
                return f"{parent.alias}.{col.raw_name}"
            else:
                return f"{parent}.{col.raw_name}"

        lineage_paths = []

        try:
            for path in runner.get_column_lineage():
                formatted_path = [format_column(col) for col in path]
                lineage_paths.append(ColumnLineagePath(path=formatted_path))
        except Exception as e:
            logger.warning(f"Error extracting column lineage paths: {e}")
            self.warnings.append(f"Column lineage path extraction warning: {str(e)}")

        return lineage_paths
