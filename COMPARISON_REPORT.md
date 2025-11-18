# SQLLineage Repository Comparison Report

## Executive Summary

This report compares two SQLLineage repository versions:
- **openmetadata-sqllineage** (master branch) - Version 1.1.2.0, based on v1.3.7 with 43 additional commits
- **reata/sqllineage** (v1.5.6 tag) - Version 1.5.6, the latest stable release

## Version Timeline

```
reata/sqllineage: v1.3.7 (Feb 2023) → v1.4.x → v1.5.x → v1.5.6 (Dec 2024)
                          ↓
openmetadata-sqllineage:  Fork + 43 commits → v1.1.2.0 (Aug 2023)
```

**Key Finding:** The openmetadata fork diverged from reata/sqllineage at v1.3.7 and has been independently developed, while reata continued development through v1.4.x and v1.5.x releases (94 commits from v1.3.7 to v1.5.6).

---

## 1. Changelog Comparison

### reata/sqllineage v1.3.7 → v1.5.6 (94 commits)

#### Major Features Added (v1.5.x series):
- **Metadata Provider Support** (v1.5.0)
  - SQLAlchemy-based MetaDataProvider (#516)
  - Wildcard expansion with MetadataProvider (#515)
  - Configure DEFAULT_SCHEMA (#532)
  - Set sqlalchemy_url through CLI option (#533)
  - Set target table's column using metadata (#557)
  - Set default schema at runtime (#555)

- **Parser Improvements**
  - Made ANSI the default dialect (#519)
  - Respect sqlfluff configuration file (#582)
  - Read nested sqlfluff config files (#637)
  - Silent mode to skip not supported statements (#509)

- **SQL Dialect Support**
  - Redshift UNLOAD statement (#723)
  - Teradata title phrase (#722)
  - BigQuery optional INTO keyword (#694)
  - TSQL identifier enclosed in brackets (#619)

- **Column Lineage Enhancements**
  - UPDATE statement column lineage (#487, #524)
  - Allow multiple sources for column lineage (#561)
  - Get column lineage exclude subquery (#543)
  - Use table alias as column lineage output (#724)
  - Lateral column alias reference (#521)

- **SQL Parser Upgrades**
  - Upgraded to sqlfluff 3.0.x (#593)
  - Upgraded to sqlfluff 3.3.0 (#660)
  - Upgraded to sqlfluff 3.4.0 (#701)
  - Upgraded to sqlfluff 3.4.2 (#710)
  - Unpinned sqlparse and sqlfluff for flexible dependency (#718)
  - Upgraded to sqlparse 0.5.0 (#595)

- **Build System Migration**
  - Migrated from setup.py to pyproject.toml
  - Switched to hatchling as build backend
  - Replaced flake8 with ruff (#692)
  - Added prettier as JS code formatter

#### Bug Fixes (v1.5.x):
- Nested UNION inside bracketed set_expression (#726)
- Case when subqueries in select_clause (#560)
- CTE and table alias case-insensitivity (#550)
- Missing target table for select into with union (#572)
- Not fully processed top-level subquery in DML (#565)
- Exception for lateral subquery (#615)
- Handling scalar subquery in function (#617)
- Metadata masked by update statement (#581)
- Parse column level lineage incorrect (#585)
- Consistent lineage results (#661)

### openmetadata-sqllineage (43 commits from v1.3.7)

#### Major Features Added:
1. **SQLFluff Parser Integration** (Initial PR #1)
   - Complete implementation of sqlfluff-based parser as an alternative to sqlparse
   - Added `sqllineage/core/parser/sqlfluff/` module with full parser implementation
   - Support for multiple SQL dialects through sqlfluff
   - Dialect-aware lineage design
   - CLI option to choose between sqlparse and sqlfluff parsers

2. **Column Level Lineage Improvements**
   - Improved column level lineage for INSERT & CREATE queries (sqlfluff) (#371)
   - Added target_column as property
   - Added target columns as graph edge
   - Comprehensive test coverage in test_sqlfluff.py

3. **SQL Dialect Specific Fixes**
   - Fixed lineage parsing for MSSQL (#19)
   - PostgreSQL style type cast support (#367)
   - Support for CREATE TABLE..CLONE and ALTER TABLE...SWAP (#372)

4. **Union Query Handling**
   - Fixed complex union subqueries with CREATE VIEW (#17)
   - Fixed CTE at the start of query in DML (#369)

5. **Frontend Enhancements**
   - Click to lock highlighted nodes (#323)
   - Use curved lines in the graph (#321)
   - Send lineage request with dialect from localStorage (#388)

6. **Bug Fixes**
   - Parenthesis around arithmetic operation (#366)
   - Missing column lineage for select distinct (#365)
   - Unnest function call with extra space (#309)

#### Version Bumps:
- Pinned sqlparse to 0.4.3 (for stability)
- Upgraded sqlfluff to 2.1.2 (#15)
- Upgraded sqlfluff to 2.1.4 (#21)

---

## 2. Unique Features in openmetadata-sqllineage NOT in reata/sqllineage v1.5.6

### Critical Unique Features:

#### 1. **Enhanced MSSQL Support** (Commit 7d44c97)
- Specific fixes for Microsoft SQL Server dialect lineage parsing
- Modified `sqllineage/core/parser/sqlfluff/handlers/target.py`
- Modified `sqllineage/core/parser/sqlfluff/utils.py`
- Added comprehensive MSSQL test cases in `tests/test_others_dialect_specific.py`

**Status:** This specific MSSQL fix is NOT present in reata v1.5.6

#### 2. **Complex Union Subqueries with CREATE VIEW** (Commit 61aee13)
- Specialized handling for complex UNION queries within CREATE VIEW statements
- Modified `sqllineage/core/parser/sqlfluff/utils.py` with union-specific logic
- Added 49 new test cases in `tests/test_columns.py`

**Status:** While reata v1.5.6 has some union fixes (#726), this specific CREATE VIEW + complex union fix appears to be openmetadata-specific

#### 3. **Enhanced INSERT/CREATE Column Lineage (sqlfluff)** (Commit 10bec6d)
- Improved column-level lineage extraction for INSERT and CREATE queries when using sqlfluff parser
- Simplified SourceHandlerMixin logic
- Simplified index store and query mechanisms
- Modified:
  - `sqllineage/core/holders.py` (33 additions)
  - `sqllineage/core/parser/sqlfluff/extractors/dml_insert_extractor.py` (84 changes)
  - `sqllineage/core/parser/sqlfluff/handlers/target.py` (16 additions)
- Added 128 new test cases in `tests/test_sqlfluff.py`

**Status:** While reata v1.5.6 has UPDATE statement column lineage (#524), the specific INSERT/CREATE enhancements from openmetadata appear different in implementation

#### 4. **Code Structure Differences**
- **openmetadata** uses `sqllineage/sqlfluff_core/` directory structure
- **reata v1.5.6** uses `sqllineage/core/parser/sqlfluff/` directory structure
- The openmetadata fork has a different organization with separate modules:
  - `sqlfluff_core/handlers/`
  - `sqlfluff_core/extractors/`
  - `sqlfluff_core/subquery/`

#### 5. **Dependency Pinning Strategy**
- **openmetadata**: Pins specific versions for stability
  - sqlparse==0.4.3 (pinned)
  - sqlfluff==2.1.4 (pinned)
  - No sqlalchemy dependency

- **reata v1.5.6**: Uses flexible version ranges
  - sqlparse>=0.5.0
  - sqlfluff>=3.2.0
  - sqlalchemy>=2.0.0 (new dependency)

---

## 3. Features in reata/sqllineage v1.5.6 NOT in openmetadata-sqllineage

### Major Missing Features:

1. **MetadataProvider System** (Critical)
   - Complete SQLAlchemy-based metadata integration
   - Wildcard expansion using database metadata
   - Schema and catalog awareness
   - Runtime schema configuration
   - This is a MAJOR architectural feature missing from openmetadata

2. **Advanced SQL Dialect Support**
   - Redshift UNLOAD statement
   - Teradata title phrase
   - BigQuery optional INTO keyword
   - TSQL bracket identifiers

3. **Modern Build System**
   - pyproject.toml instead of setup.py
   - hatchling build backend
   - Ruff instead of flake8
   - Python 3.9+ requirement (dropped 3.7 support)

4. **Latest Parser Versions**
   - sqlfluff 3.4.2 (vs 2.1.4 in openmetadata)
   - sqlparse 0.5.0 (vs 0.4.3 in openmetadata)

5. **UPDATE Statement Column Lineage**
   - Full column-level lineage for UPDATE statements
   - Not present in openmetadata fork

6. **Multiple Source Column Lineage**
   - Support for columns derived from multiple source tables
   - Enhanced column lineage tracking

7. **Configuration File Support**
   - Respect for sqlfluff configuration files
   - Nested config file reading

---

## 4. Key Technical Differences

### Architecture

| Aspect | openmetadata-sqllineage | reata/sqllineage v1.5.6 |
|--------|------------------------|-------------------------|
| Base Version | v1.3.7 | v1.5.6 |
| Python Version | 3.7+ | 3.9+ |
| Build System | setup.py | pyproject.toml |
| SQLFluff Version | 2.1.4 (pinned) | 3.4.2+ (unpinned) |
| SQLParse Version | 0.4.3 (pinned) | 0.5.0+ (unpinned) |
| SQLAlchemy | Not included | 2.0.0+ required |
| Code Formatter | flake8 | ruff |
| Directory Structure | sqlfluff_core/ | core/parser/sqlfluff/ |

### Code Quality Tools

**openmetadata-sqllineage:**
- flake8, flake8-blind-except, flake8-builtins, flake8-import-order
- black, mypy, bandit

**reata/sqllineage v1.5.6:**
- ruff (replaces flake8)
- black 25.1.0+, mypy 1.17.1+
- No bandit

### Testing

**openmetadata-sqllineage:**
- Python 3.7, 3.8, 3.9, 3.10 support
- test_sqlfluff.py with 128 test cases for sqlfluff-specific features
- test_others_dialect_specific.py for MSSQL

**reata/sqllineage v1.5.6:**
- Python 3.9, 3.10, 3.11, 3.12, 3.13 support
- Broader dialect coverage in tests
- Metadata provider test coverage

---

## 5. Migration Considerations

### If Upgrading from openmetadata-sqllineage to reata/sqllineage v1.5.6:

**Gains:**
- MetadataProvider for database schema introspection
- Latest SQL dialect support (Redshift, Teradata, BigQuery enhancements)
- UPDATE statement column lineage
- Modern build system and tooling
- Latest sqlfluff (3.4.2) with bug fixes and new features
- Better configuration file support
- Active maintenance and continued development

**Potential Issues:**
- Need to migrate from Python 3.7 to 3.9+
- Need to add sqlalchemy dependency
- May lose specific MSSQL fixes from openmetadata
- May lose specific CREATE VIEW + complex union handling
- Code using old API paths may need updates
- Different dependency pinning strategy (may cause compatibility issues)

### If Staying with openmetadata-sqllineage:

**Advantages:**
- Stable pinned dependencies (less risk of breaking changes)
- Specific MSSQL handling
- Enhanced CREATE VIEW with complex union support
- Python 3.7 compatibility if needed

**Disadvantages:**
- Missing 94 commits of improvements from reata
- No MetadataProvider support
- Outdated sqlfluff version (2.1.4 vs 3.4.2)
- No UPDATE statement column lineage
- Limited future development (fork appears less active)
- Missing modern SQL dialect features

---

## 6. Recommendations

### For New Projects:
**Use reata/sqllineage v1.5.6** because:
- It's actively maintained with regular releases
- Includes the MetadataProvider system for advanced use cases
- Has the latest parser versions with bug fixes
- Supports modern Python versions (3.9-3.13)
- Has flexible dependency management
- Includes more SQL dialect support

### For Existing openmetadata-sqllineage Users:

**Consider migrating if:**
- You need MetadataProvider functionality
- You need UPDATE statement column lineage
- You need support for newer SQL dialects (Redshift, Teradata, BigQuery)
- You want the latest parser bug fixes
- You can upgrade to Python 3.9+

**Stay with openmetadata if:**
- You specifically need the MSSQL fixes
- You rely on the specific CREATE VIEW + complex union handling
- You need Python 3.7 compatibility
- You prefer pinned dependencies for stability
- Your use case is working well with current version

### For Merging Features:

The openmetadata fork contains at least **3 valuable features** that could be contributed back to reata/sqllineage:

1. **MSSQL-specific lineage parsing fixes** (Commit 7d44c97)
2. **Complex union subqueries with CREATE VIEW** (Commit 61aee13)
3. **Enhanced INSERT/CREATE column lineage for sqlfluff** (Commit 10bec6d)

These could be valuable contributions to the upstream project if properly isolated and submitted as pull requests.

---

## 7. Conclusion

The **reata/sqllineage v1.5.6** is significantly ahead of the openmetadata fork in terms of:
- Feature completeness (MetadataProvider)
- Code modernization (Python 3.9+, ruff, pyproject.toml)
- Parser versions (sqlfluff 3.4.2 vs 2.1.4)
- SQL dialect support
- Active development

However, the **openmetadata-sqllineage** fork contains specific valuable features:
- MSSQL-specific fixes
- CREATE VIEW + complex union handling
- Some unique column lineage improvements

For most users, **reata/sqllineage v1.5.6 is the recommended choice** due to its active maintenance, modern architecture, and comprehensive feature set. The openmetadata-specific features could potentially be contributed upstream to benefit the entire community.

---

## Appendix: Commit Statistics

- **reata v1.3.7 → v1.5.6**: 94 commits
- **openmetadata fork (from v1.3.7)**: 43 commits
- **Common ancestor**: v1.3.7 (e34c6b8)
- **Total divergence**: 137 unique commits across both branches

### Key Contributors

**reata/sqllineage:**
- Reata (reddevil.hjw@gmail.com) - Primary maintainer
- Multiple community contributors

**openmetadata-sqllineage:**
- OpenMetadata Committers
- Pere Miquel Brull
- Mayur Singal
- Nahuel (@getcollate.io)
