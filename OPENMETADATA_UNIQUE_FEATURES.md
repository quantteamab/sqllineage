# OpenMetadata-SQLLineage Unique Features Not Merged into reata/sqllineage v1.5.6

## Overview

This document identifies specific features and fixes that exist in the openmetadata-sqllineage fork but have NOT been merged into the upstream reata/sqllineage v1.5.6 release.

---

## 1. MSSQL-Specific Lineage Parsing Fix

**Commit:** 7d44c97efee0b9d7f8be9b914aa7f7d9cc4cd285
**PR:** #19
**Author:** Mayur Singal
**Date:** Aug 17, 2023

### Changes:
```
sqllineage/core/parser/sqlfluff/handlers/target.py |  2 +-
sqllineage/core/parser/sqlfluff/utils.py           |  6 +++++-
sqllineage/utils/helpers.py                        |  2 +-
tests/test_others_dialect_specific.py              | 17 +++++++++++++++++
```

### Description:
- Specific fixes to handle Microsoft SQL Server dialect parsing
- Added MSSQL-specific test cases
- Modified target handler to correctly process MSSQL syntax
- Enhanced utility functions for MSSQL compatibility

### Impact:
Users relying on MSSQL lineage parsing may encounter issues with reata v1.5.6 that are fixed in the openmetadata fork.

### Recommendation:
This fix should be extracted and submitted as a PR to reata/sqllineage.

---

## 2. Complex Union Subqueries with CREATE VIEW

**Commit:** 61aee13 (ac4dd9f - merge commit)
**PR:** #17
**Author:** Pere Miquel Brull
**Date:** Jul 13, 2023

### Changes:
```
sqllineage/core/parser/sqlfluff/utils.py | 12 ++++----
tests/test_columns.py                    | 49 ++++++++++++++++++++++++++++++++
```

### Description:
- Handles complex UNION queries within CREATE VIEW statements
- Modified sqlfluff utility functions to properly extract lineage from nested union operations
- Added 49 comprehensive test cases covering various union scenarios

### Technical Details:
The fix modifies how subqueries are extracted when UNION operations are combined with CREATE VIEW statements, ensuring proper column-level lineage is maintained through complex query structures.

### Comparison with reata v1.5.6:
While reata v1.5.6 includes fix #726 for "nested UNION inside bracketed set_expression", the specific handling of CREATE VIEW + complex unions from openmetadata appears to use a different approach and may cover additional edge cases.

### Impact:
Users with CREATE VIEW statements containing complex UNION subqueries may get more accurate lineage results with the openmetadata version.

---

## 3. Enhanced Column-Level Lineage for INSERT & CREATE Queries (SQLFluff)

**Commit:** 10bec6d1a40f2c68c826ddccd1a96d9853c41440
**PR:** #371
**Author:** Mayur Singal (with Reata co-authorship)
**Date:** Jun 11, 2023

### Changes:
```
sqllineage/core/holders.py                         |  33 +++++-
sqllineage/core/models.py                          |   9 +-
sqllineage/core/parser/__init__.py                 |  12 +-
sqlfluff/extractors/dml_insert_extractor.py        |  84 +++++++-------
extractors/lineage_holder_extractor.py             |   4 +
sqllineage/core/parser/sqlfluff/handlers/target.py |  16 +++
sqllineage/utils/constant.py                       |   4 +
tests/test_insert.py                               |  18 +--
tests/test_others.py                               |  10 --
tests/test_sqlfluff.py                             | 128 +++++++++++++++++++++
```

Total: 243 insertions, 75 deletions

### Description:
This is a major enhancement focused on improving column-level lineage extraction specifically when using the sqlfluff parser for INSERT and CREATE queries.

### Key Improvements:

1. **Target Column Property**
   - Added target_column as a property to models
   - Target columns now appear as graph edges
   - Better column-to-column lineage mapping

2. **Refactored SourceHandlerMixin**
   - Simplified logic for source column detection
   - Better handling of subqueries in INSERT statements

3. **Improved DmlInsertExtractor**
   - 84 lines refactored for better column extraction
   - Handles parenthesized union test cases
   - Better index store and query mechanisms

4. **Comprehensive Testing**
   - Created dedicated test_sqlfluff.py with 128 test cases
   - Moved sqlfluff-specific tests from generic test files
   - Added tests for:
     - Multiple CASE WHEN with subqueries
     - CTE column references
     - Set expressions as subqueries
     - Complex INSERT scenarios

### Comparison with reata v1.5.6:

**reata v1.5.6 has:**
- UPDATE statement column lineage (#487, #524)
- Multiple sources for column lineage (#561)
- General column lineage improvements

**openmetadata has:**
- Specific INSERT/CREATE enhancements for sqlfluff parser
- Different implementation approach in DmlInsertExtractor
- More extensive test coverage for INSERT scenarios (128 tests in test_sqlfluff.py)

The implementations appear to diverge in approach. While both aim to improve column lineage, the openmetadata version focuses specifically on INSERT/CREATE with sqlfluff, while reata v1.5.6 expanded to UPDATE statements and multiple source handling.

### Impact:
Users parsing INSERT and CREATE statements with the sqlfluff parser may get different (potentially more accurate for specific cases) column-level lineage with the openmetadata version.

---

## 4. Frontend User Experience Enhancements

### A. Click to Lock Highlighted Nodes
**Commit:** 200c96f
**PR:** #323
**Date:** Nov 2022

**Description:**
Allows users to click and lock nodes in the lineage visualization graph, preventing them from being deselected when hovering over other nodes.

### B. Curved Lines in Graph Visualization
**Commit:** e940cbe
**PR:** #321
**Date:** Nov 2022

**Description:**
Changed graph visualization to use curved lines instead of straight lines for better visual clarity and aesthetics.

### C. Dialect Selection from localStorage
**Commit:** 8ed0e52
**PR:** #388
**Date:** Early 2023

**Description:**
Frontend can send lineage requests with dialect preference stored in browser localStorage, allowing users to maintain their preferred SQL dialect across sessions.

### Impact:
These frontend enhancements improve user experience but are not present in reata v1.5.6's visualization.

---

## 5. Additional SQL Feature Support

### PostgreSQL Style Type Cast
**Commit:** c7be506
**PR:** #367
**Date:** 2022-2023

**Description:**
Added support for PostgreSQL-style type casting syntax (e.g., `::integer`).

**Status in reata v1.5.6:** Unknown - would need to verify if this specific syntax is supported.

### CREATE TABLE...CLONE and ALTER TABLE...SWAP
**Commit:** 8882d4a
**PR:** #372
**Date:** 2022-2023

**Description:**
Support for Snowflake-specific operations:
- CREATE TABLE ... CLONE (table cloning)
- ALTER TABLE ... SWAP (partition swapping)

**Status in reata v1.5.6:**
- Swap partitions support exists but may be Vertica-only (#616)
- Clone syntax may not be supported

---

## 6. Bug Fixes Potentially Missing in reata v1.5.6

### Missing Column Lineage for SELECT DISTINCT
**Commit:** 6351f91
**PR:** #365

**Description:**
Fixed an issue where SELECT DISTINCT queries were not properly tracking column lineage.

**Status:** May be fixed differently in reata v1.5.6, needs verification.

### Parenthesis Around Arithmetic Operations
**Commit:** c568aed
**PR:** #366

**Description:**
Fixed parsing issues when arithmetic operations are enclosed in parentheses.

**Status:** May be fixed differently in reata v1.5.6, needs verification.

---

## 7. Dependency Strategy Differences

### openmetadata-sqllineage Approach:
```python
install_requires=[
    "sqlparse==0.4.3",      # Pinned for stability
    "networkx>=2.4",
    "sqlfluff==2.1.4",      # Pinned for stability
]
```

**Philosophy:**
- Pin specific versions for stability
- Avoid breaking changes from dependency updates
- Tested specifically against these versions

### reata v1.5.6 Approach:
```python
dependencies = [
    "sqlparse>=0.5.0",      # Flexible, allow updates
    "networkx>=2.4",
    "sqlfluff>=3.2.0",      # Flexible, allow updates
    "sqlalchemy>=2.0.0",    # New dependency
]
```

**Philosophy:**
- Allow dependency updates within major versions
- Users can benefit from bug fixes in dependencies
- More flexible but potentially less stable

### Impact:
- openmetadata users have more predictable behavior
- reata users get latest dependency fixes but may encounter breaking changes

---

## 8. Code Organization Differences

### openmetadata-sqllineage Structure:
```
sqllineage/
  ├── sqlfluff_core/          # Separate module for sqlfluff
  │   ├── handlers/
  │   ├── subquery/
  │   │   ├── cte_extractor.py
  │   │   ├── dml_insert_extractor.py
  │   │   ├── dml_select_extractor.py
  │   │   └── ...
  │   └── utils/
  └── core/                   # Original sqlparse-based core
```

### reata v1.5.6 Structure:
```
sqllineage/
  └── core/
      └── parser/
          ├── sqlfluff/       # Integrated into core
          │   ├── extractors/
          │   │   ├── create_insert.py
          │   │   ├── select.py
          │   │   └── ...
          │   └── ...
          └── sqlparse/       # Integrated into core
```

### Impact:
- Different import paths between versions
- Code migration between versions requires path updates
- reata's structure is more unified

---

## Summary Table of Unique Features

| Feature | Present in openmetadata | Present in reata v1.5.6 | Recommendation |
|---------|------------------------|-------------------------|----------------|
| MSSQL-specific fixes | ✅ Yes | ❌ No | Submit to upstream |
| Complex union + CREATE VIEW | ✅ Yes | ⚠️ Different approach | Verify compatibility |
| INSERT/CREATE lineage (sqlfluff) | ✅ Yes | ⚠️ Different implementation | Compare effectiveness |
| Click-to-lock nodes (UI) | ✅ Yes | ❌ No | Nice-to-have |
| Curved lines (UI) | ✅ Yes | ❌ No | Nice-to-have |
| Dialect in localStorage | ✅ Yes | ❌ No | Submit to upstream |
| PostgreSQL type cast | ✅ Yes | ❓ Unknown | Verify |
| CREATE TABLE...CLONE | ✅ Yes | ❌ No | Submit to upstream |
| SELECT DISTINCT fix | ✅ Yes | ❓ Unknown | Verify |
| Parenthesis arithmetic fix | ✅ Yes | ❓ Unknown | Verify |
| Pinned dependencies | ✅ Yes | ❌ No | Different philosophy |

---

## Recommendations for Feature Integration

### High Priority (Should be contributed to reata/sqllineage):

1. **MSSQL-specific lineage parsing fix** (#19)
   - Clear improvement for MSSQL users
   - Well-tested
   - Minimal code changes

2. **Dialect selection in localStorage** (#388)
   - Improves UX
   - No breaking changes

3. **CREATE TABLE...CLONE support** (#372)
   - Useful for Snowflake users
   - Extends SQL dialect coverage

### Medium Priority (Needs verification):

1. **Complex union + CREATE VIEW handling** (#17)
   - Verify if reata's approach (#726) covers the same cases
   - May have overlap with existing fixes

2. **INSERT/CREATE column lineage enhancements** (#371)
   - Significant changes
   - May conflict with reata's UPDATE lineage work
   - Needs careful comparison

### Low Priority (Nice-to-have):

1. **Frontend UI improvements** (#321, #323)
   - Subjective improvements
   - May not align with upstream UI direction

2. **Bug fixes** (#365, #366)
   - May already be fixed in v1.5.6 through other commits
   - Needs verification

---

## Testing Recommendations

If migrating from openmetadata to reata v1.5.6, test these scenarios:

1. **MSSQL queries** - May break
2. **CREATE VIEW with complex UNION** - May behave differently
3. **INSERT statements with column lineage** - May behave differently
4. **Frontend dialect selection** - Will not persist
5. **Graph visualization** - Will look different (straight vs curved lines)

---

## Conclusion

The openmetadata-sqllineage fork contains **3-5 significant unique features** that are not present in reata/sqllineage v1.5.6:

1. MSSQL-specific fixes (confirmed unique)
2. Complex union handling with CREATE VIEW (likely unique or different approach)
3. Enhanced INSERT/CREATE lineage for sqlfluff (different implementation)
4. Frontend UX improvements (confirmed unique)
5. CREATE TABLE...CLONE support (likely unique)

These features represent valuable contributions that could benefit the upstream project if properly isolated and submitted as pull requests.
