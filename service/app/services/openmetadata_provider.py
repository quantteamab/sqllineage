"""OpenMetadata integration for metadata provider."""

import logging
import time
from typing import Optional

import requests

from sqllineage.core.metadata_provider import MetaDataProvider

logger = logging.getLogger(__name__)


class OpenMetadataProvider(MetaDataProvider):
    """
    OpenMetadataProvider queries metadata from OpenMetadata API.

    This provider fetches table column information from OpenMetadata
    and caches the results to minimize API calls.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 10,
        cache_ttl: int = 300,
    ):
        """
        Initialize OpenMetadata provider.

        :param base_url: OpenMetadata API base URL (e.g., https://openmetadata.example.com/api/v1)
        :param api_key: API key for authentication
        :param timeout: Request timeout in seconds
        :param cache_ttl: Cache time-to-live in seconds
        """
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._cache: dict[str, tuple[list[str], float]] = {}
        self._connected = False
        self._test_connection()

    def _test_connection(self) -> None:
        """Test connection to OpenMetadata API."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                f"{self.base_url}/system/status",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            self._connected = True
            logger.info("Successfully connected to OpenMetadata API")
        except Exception as e:
            logger.warning(f"Failed to connect to OpenMetadata API: {e}")
            self._connected = False

    def _get_table_columns(self, schema: str, table: str, **kwargs) -> list[str]:
        """
        Get table columns from OpenMetadata API.

        :param schema: Database or schema name
        :param table: Table name
        :return: List of column names
        """
        if not self._connected:
            logger.warning(
                "OpenMetadata not connected, returning empty column list for %s.%s",
                schema,
                table,
            )
            return []

        cache_key = f"{schema}.{table}"

        # Check cache
        if cache_key in self._cache:
            columns, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(
                    "Cache hit for %s.%s, returning %d columns",
                    schema,
                    table,
                    len(columns),
                )
                return columns

        # Fetch from API
        try:
            columns = self._fetch_table_columns(schema, table)
            self._cache[cache_key] = (columns, time.time())
            logger.debug(
                "Fetched %d columns for %s.%s from OpenMetadata",
                len(columns),
                schema,
                table,
            )
            return columns
        except Exception as e:
            logger.warning(
                "Error fetching columns for %s.%s from OpenMetadata: %s",
                schema,
                table,
                e,
            )
            return []

    def _fetch_table_columns(self, schema: str, table: str) -> list[str]:
        """
        Fetch table columns from OpenMetadata API.

        OpenMetadata API structure:
        GET /tables/name/{fqn}
        where fqn is fully qualified name: service.database.schema.table

        :param schema: Database or schema name
        :param table: Table name
        :return: List of column names
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Try multiple FQN patterns as OpenMetadata structure can vary
        # Pattern 1: database.schema.table
        # Pattern 2: schema.table
        # Pattern 3: just table
        fqn_patterns = [
            f"{schema}.{table}",
            table,
        ]

        for fqn in fqn_patterns:
            try:
                url = f"{self.base_url}/tables/name/{fqn}"
                response = requests.get(url, headers=headers, timeout=self.timeout)

                if response.status_code == 200:
                    data = response.json()
                    columns = [col["name"] for col in data.get("columns", [])]
                    if columns:
                        return columns
                elif response.status_code != 404:
                    logger.warning(
                        "Unexpected status %d for FQN %s: %s",
                        response.status_code,
                        fqn,
                        response.text,
                    )
            except Exception as e:
                logger.debug("Failed to fetch with FQN %s: %s", fqn, e)

        logger.warning(
            "Could not find table %s.%s in OpenMetadata with any FQN pattern",
            schema,
            table,
        )
        return []

    def __bool__(self):
        """Return True if provider is connected and ready."""
        return self._connected

    def clear_cache(self) -> None:
        """Clear the metadata cache."""
        self._cache.clear()
        logger.info("Cleared OpenMetadata cache")
