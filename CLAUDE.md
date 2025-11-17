# CLAUDE.md - SQLLineage Development Guide for AI Assistants

## Project Overview

**SQLLineage** is a production-ready SQL lineage analysis tool that extracts table-level and column-level lineage from SQL statements without requiring database connectivity. It supports multiple SQL dialects and provides both CLI and web visualization interfaces.

- **Language**: Python 3.10+ (Primary), JavaScript/React (Frontend)
- **License**: MIT
- **Maturity**: Production/Stable (v1.5.6)
- **Key Technologies**: sqlparse, sqlfluff, networkx, sqlalchemy, React, Vite

## Repository Structure

```
sqllineage/
├── .github/
│   └── workflows/          # CI/CD pipelines (build, publish)
├── docs/                   # Sphinx documentation
├── sqllineage/            # Main Python package
│   ├── __init__.py        # Version, constants, defaults
│   ├── cli.py             # Command-line interface entry point
│   ├── runner.py          # LineageRunner - main API entry point
│   ├── drawing.py         # Visualization web server
│   ├── io.py              # Cytoscape format conversion
│   ├── config.py          # Configuration management
│   ├── exceptions.py      # Custom exceptions
│   ├── core/              # Core lineage analysis logic
│   │   ├── holders.py     # SQLLineageHolder - lineage graph container
│   │   ├── models.py      # Table, Column, SubQuery, Path models
│   │   ├── analyzer.py    # Abstract analyzer interface
│   │   ├── metadata/      # Metadata providers (dummy, sqlalchemy)
│   │   └── parser/        # SQL parsers
│   │       ├── sqlfluff/  # Primary parser (supports 20+ dialects)
│   │       │   ├── analyzer.py      # SqlFluffLineageAnalyzer
│   │       │   ├── models.py        # AST models
│   │       │   ├── extractors/      # Statement-specific extractors
│   │       │   │   ├── base.py      # BaseExtractor
│   │       │   │   ├── select.py    # SELECT statement
│   │       │   │   ├── create_insert.py  # INSERT/CREATE
│   │       │   │   ├── merge.py     # MERGE statement
│   │       │   │   ├── update.py    # UPDATE statement
│   │       │   │   └── ...
│   │       │   └── utils.py
│   │       └── sqlparse/  # Legacy parser (deprecated)
│   │           ├── analyzer.py
│   │           ├── models.py
│   │           └── handlers/
│   ├── utils/             # Utility functions
│   └── data/              # Sample SQL files (e.g., TPC-DS)
├── sqllineagejs/          # React frontend for visualization
│   ├── src/               # React components
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite build configuration
├── tests/                 # Test suite
│   ├── core/              # Core functionality tests
│   ├── sql/               # SQL parsing tests
│   │   ├── table/         # Table-level lineage tests
│   │   └── column/        # Column-level lineage tests
│   └── helpers.py         # Test utilities and assertions
├── pyproject.toml         # Python package configuration (Hatch)
├── hatch_build.py         # Custom build hook for JS assets
├── .pre-commit-config.yaml # Pre-commit hooks
└── CONTRIBUTING.md        # Development guidelines

```

## Development Environment Setup

### Prerequisites
- **Python**: 3.10+ (recommend using minimum supported version 3.10 for development)
- **Node.js**: 20+ (for frontend development)
- **Tools**: tox, git, pre-commit (optional)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/reata/sqllineage.git
cd sqllineage

# Create development environment with all dependencies using tox
tox -e py310 --devenv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Node dependencies for frontend (if modifying sqllineagejs)
cd sqllineagejs
npm install
cd ..

# Optional: Set up pre-commit hooks for automatic code quality checks
pip install pre-commit
pre-commit install
```

### Running the Application Locally

```bash
# Run CLI on a SQL file
sqllineage -f path/to/file.sql

# Run CLI with inline SQL
sqllineage -e "INSERT INTO table1 SELECT * FROM table2"

# Launch visualization web server
sqllineage -g -f path/to/file.sql

# Run with specific dialect
sqllineage -e "SELECT * FROM table" --dialect=sparksql

# Column-level lineage
sqllineage -f file.sql -l column
```

## Code Standards and Quality Tools

SQLLineage enforces strict code quality standards through automated tooling:

### 1. **black** - Code Formatting
- Line length: 120 characters
- Automatic formatting for consistent style
- Run: `black .`
- Check without modifying: `black . --check --diff`

### 2. **ruff** - Linting
- Fast Python linter replacing flake8, isort, etc.
- Configuration in `pyproject.toml` under `[tool.ruff]`
- Selected rules: E, F, A (builtins), G (logging), I (imports), UP (syntax upgrades)
- Ignored: A005 (stdlib-module-shadowing - intentional for parser, copy, select, io modules)
- Run: `ruff check .`
- Auto-fix: `ruff check . --fix`

### 3. **mypy** - Type Checking
- Strict type checking enforced
- Configuration in `pyproject.toml` under `[tool.mypy]`
- Key settings:
  - `disallow_untyped_calls = true`
  - `warn_return_any = true`
  - `disallow_any_generics = true`
  - `strict_optional = true`
- Run: `mypy`
- **Important**: All code must include type annotations

### 4. **pytest** - Testing
- Comprehensive test suite with high coverage requirements
- Configuration in `pyproject.toml` under `[tool.coverage]`
- Run: `pytest`
- With coverage: `pytest --cov`
- Coverage source: `sqllineage/` directory

### Running All Quality Checks

```bash
# Run all checks locally (same as CI)
tox -e py310

# Or run individual tools
black . --check --diff
ruff check .
mypy
pytest --cov

# Run across all supported Python versions (if installed)
tox
```

## Testing Conventions and Patterns

### Test Organization

Tests are organized by functionality and lineage level:

```
tests/
├── core/                  # Tests for core modules
│   ├── test_runner.py     # LineageRunner tests
│   ├── test_holder.py     # SQLLineageHolder tests
│   ├── test_models.py     # Model tests
│   ├── test_parser.py     # Parser tests
│   └── ...
└── sql/                   # SQL parsing tests (dialect-specific)
    ├── table/             # Table-level lineage tests
    │   ├── test_select.py
    │   ├── test_insert.py
    │   └── ...
    └── column/            # Column-level lineage tests
        ├── test_column_select_from_join.py
        ├── test_metadata_target_column.py
        └── ...
```

### Test Helper Functions (tests/helpers.py)

The test suite provides specialized assertion helpers:

```python
from tests.helpers import assert_table_lineage_equal, assert_column_lineage_equal

# Test table-level lineage
assert_table_lineage_equal(
    sql="INSERT INTO target SELECT * FROM source",
    source_tables=["source"],
    target_tables=["target"],
    dialect="ansi",
    test_sqlfluff=True,    # Test with sqlfluff parser
    test_sqlparse=True     # Test with legacy sqlparse parser
)

# Test column-level lineage
assert_column_lineage_equal(
    sql="INSERT INTO tgt (col1) SELECT src_col FROM src",
    column_lineages=[
        (ColumnQualifierTuple("src_col", "src"), ColumnQualifierTuple("col1", "tgt"))
    ],
    dialect="sparksql",
    metadata_provider=metadata_provider  # Optional: for metadata-aware tests
)
```

### Writing Tests

**Guidelines:**
1. **Test both parsers**: Unless dialect-specific, test with both sqlfluff and sqlparse parsers
2. **Use descriptive names**: Test function names should describe the SQL scenario
3. **Organize by statement type**: Group tests by SQL statement type (SELECT, INSERT, MERGE, etc.)
4. **Dialect awareness**: Specify dialect when testing non-ANSI SQL features
5. **Metadata tests**: Use `generate_metadata_providers()` helper for metadata-dependent tests

**Example Test Pattern:**

```python
def test_insert_select_with_join():
    """Test lineage for INSERT with SELECT containing JOIN"""
    assert_table_lineage_equal(
        sql="""
        INSERT INTO target_table
        SELECT a.col1, b.col2
        FROM table_a a
        JOIN table_b b ON a.id = b.id
        """,
        source_tables=["table_a", "table_b"],
        target_tables=["target_table"],
        dialect="ansi"
    )
```

## Architecture and Key Components

### Core Architecture

SQLLineage follows a modular architecture with clear separation of concerns:

```
SQL Input → Parser (sqlfluff/sqlparse) → Extractor → Holder → Runner → Output
                                             ↓
                                       MetaDataProvider (optional)
```

### Key Components

#### 1. **LineageRunner** (sqllineage/runner.py)
- **Purpose**: Main API entry point for lineage analysis
- **Responsibilities**:
  - Splits SQL into individual statements
  - Selects appropriate parser based on dialect
  - Orchestrates analysis through analyzers
  - Aggregates lineage from multiple statements
  - Provides lazy evaluation for performance
- **Key Methods**:
  - `source_tables`, `target_tables`, `intermediate_tables` (properties)
  - `get_column_lineage()` - returns column-level lineage paths
  - `print_table_lineage()`, `print_column_lineage()` - CLI output
  - `to_cytoscape()` - converts to graph format for visualization
  - `draw()` - launches visualization web server

#### 2. **SQLLineageHolder** (sqllineage/core/holders.py)
- **Purpose**: Container for lineage information using NetworkX graphs
- **Graph Structure**:
  - Table graph: Directed graph of Table nodes
  - Column graph: Directed graph of Column nodes (with Table parents)
- **Key Methods**:
  - `add_read()`, `add_write()` - track table reads/writes
  - `add_column_lineage()` - track column dependencies
  - `get_column_lineage()` - compute lineage paths through graph traversal

#### 3. **Analyzers** (sqllineage/core/parser/*/analyzer.py)
- **SqlFluffLineageAnalyzer**: Primary analyzer supporting 20+ SQL dialects
- **SqlParseLineageAnalyzer**: Legacy analyzer (deprecated, `non-validating` dialect)
- **Responsibilities**:
  - Parse SQL into AST (Abstract Syntax Tree)
  - Delegate to appropriate Extractor based on statement type
  - Return SQLLineageHolder with lineage information

#### 4. **Extractors** (sqllineage/core/parser/sqlfluff/extractors/)
- **BaseExtractor**: Abstract base class for all extractors
- **Statement-specific extractors**:
  - `SelectExtractor`: Handles SELECT statements (most complex)
  - `CreateInsertExtractor`: INSERT, CREATE TABLE AS SELECT
  - `MergeExtractor`: MERGE statements
  - `UpdateExtractor`: UPDATE statements
  - `CTEExtractor`: Common Table Expressions (WITH clause)
  - `RenameExtractor`: ALTER TABLE RENAME
  - `DropExtractor`: DROP TABLE
  - etc.
- **Pattern**: Each extractor walks the AST and populates a holder with lineage info

#### 5. **Models** (sqllineage/core/models.py)
- **Table**: Represents a table with optional schema/database qualifiers
  - Format: `database.schema.table` or `schema.table` or `table`
  - Handles special cases: CTE tables, temporary tables
- **Column**: Represents a column with parent Table
  - Supports wildcard columns (`*`, `table.*`)
- **SubQuery**: Represents subquery aliases
- **Path**: Represents lineage path between columns

#### 6. **MetaDataProvider** (sqllineage/core/metadata_provider.py)
- **DummyMetaDataProvider**: No-op provider (default)
- **SQLAlchemyMetaDataProvider**: Connects to database for schema metadata
- **Purpose**: Resolves ambiguous column references, expands wildcards
- **Usage**: `sqllineage -f file.sql --sqlalchemy_url=postgresql://user:pass@host/db`

### Design Patterns

1. **Lazy Evaluation**: LineageRunner uses `@lazy_property` decorator to defer expensive operations
2. **Visitor Pattern**: Extractors traverse AST nodes using visitor-like pattern
3. **Strategy Pattern**: Different parsers (sqlfluff vs sqlparse) implement common Analyzer interface
4. **Factory Pattern**: Extractor selection based on statement type
5. **Graph-based Lineage**: Uses NetworkX for complex lineage path computations

## Development Workflow

SQLLineage follows **GitHub Flow** with issue-driven development:

### 1. Issue Creation
- All work starts with a GitHub issue
- Issues are labeled and assigned to milestones
- Discuss implementation approach in issue comments

### 2. Branch Development
- Fork the repository
- Create feature branch: `git checkout -b feature/your-feature-name`
- Make changes with clear, atomic commits
- Follow commit message conventions (imperative mood, concise)

### 3. Code Quality
- Run quality checks locally: `tox -e py310`
- Ensure all tests pass: `pytest --cov`
- Pre-commit hooks automatically run black, ruff, mypy
- Fix any linting or type errors before committing

### 4. Pull Request Submission

**Before submitting:**
- [ ] All tests pass locally
- [ ] Code coverage maintained or improved
- [ ] Type annotations added for new code
- [ ] Documentation updated if needed
- [ ] Rebase on latest master (no conflicts)
- [ ] GitHub Actions CI passes

**PR Description should include:**
- Link to related issue
- Summary of changes
- Testing approach
- Breaking changes (if any)

### 5. Code Review
- Maintainer reviews PR
- Address feedback with additional commits
- Once approved, maintainer merges to master

## Building and Deployment

### Python Package Build

```bash
# Build distribution packages
pip install hatch
hatch build

# This creates:
# dist/sqllineage-X.Y.Z-py3-none-any.whl
# dist/sqllineage-X.Y.Z.tar.gz
```

**Note**: `hatch_build.py` is a custom build hook that builds the React frontend and includes it in the Python package under `sqllineage/build/`.

### Frontend Build

```bash
cd sqllineagejs
npm run build  # Creates build/ directory with production assets
```

### Release Process

1. **Update version** in both:
   - `sqllineage/__init__.py` (VERSION variable)
   - `sqllineagejs/package.json` (version field)

2. **Update CHANGELOG** in docs/release_note/

3. **Create Git tag** and GitHub release:
   - Tag format: `vX.Y.Z` (e.g., `v1.5.6`)
   - GitHub Actions automatically publishes to PyPI on release creation

4. **Verify deployment**:
   - Check PyPI: https://pypi.org/project/sqllineage/
   - Test installation: `pip install sqllineage==X.Y.Z`

## Common Tasks for AI Assistants

### Adding Support for a New SQL Statement Type

1. Create new extractor in `sqllineage/core/parser/sqlfluff/extractors/`
2. Inherit from `BaseExtractor`
3. Implement `extract()` method to populate holder
4. Register extractor in `SqlFluffLineageAnalyzer`
5. Add comprehensive tests in `tests/sql/table/` and `tests/sql/column/`

### Adding a New SQL Dialect

1. Check if sqlfluff supports the dialect
2. Add dialect to `SqlFluffLineageAnalyzer.SUPPORTED_DIALECTS`
3. Handle dialect-specific keywords/syntax in extractors
4. Add dialect-specific tests

### Fixing a Lineage Bug

1. Create failing test case reproducing the issue
2. Debug by examining AST structure (use sqlfluff's parse tree viewer)
3. Fix extractor logic to handle the case
4. Verify tests pass for both parsers (if applicable)
5. Check for similar patterns that might have same issue

### Improving Column-Level Lineage

1. Focus on `SelectExtractor` (most complex)
2. Consider metadata requirements (wildcard expansion, ambiguous columns)
3. Test with `assert_column_lineage_equal()` helper
4. Add tests with and without metadata provider

## Important Notes for AI Assistants

### DO:
- ✅ Always run `tox -e py310` before committing
- ✅ Add type annotations to all new functions/methods
- ✅ Write tests for both table and column lineage when applicable
- ✅ Test with multiple dialects if the feature is dialect-agnostic
- ✅ Use helper functions from `tests/helpers.py` for assertions
- ✅ Document complex lineage logic with comments
- ✅ Check both sqlfluff and sqlparse parsers unless dialect-specific
- ✅ Update version in both Python and JS packages for releases

### DON'T:
- ❌ Don't commit without running black, ruff, mypy
- ❌ Don't skip type annotations (mypy will fail)
- ❌ Don't ignore failing tests
- ❌ Don't modify core models without considering backward compatibility
- ❌ Don't add dependencies without discussing in issue first
- ❌ Don't hardcode dialect-specific logic in shared extractors
- ❌ Don't forget to update both parsers if fixing general SQL parsing

### Code Conventions

1. **Imports**: Organized by ruff (stdlib, third-party, local)
2. **Type Hints**: Required for all function signatures, use PEP 604 style (`str | None` instead of `Optional[str]`)
3. **Structural Pattern Matching**: Python 3.10+ match/case statements preferred where appropriate
4. **String Formatting**: Use f-strings for string interpolation
5. **Logging**: Use module-level logger: `logger = logging.getLogger(__name__)`
6. **Constants**: Define in `sqllineage/__init__.py` or appropriate module

### Testing Best Practices

1. **Parameterized Tests**: Use `pytest.mark.parametrize` for similar test cases
2. **Fixtures**: Define in conftest.py if shared across modules (currently no conftest.py)
3. **Test Data**: SQL test files can go in `tests/sql/` or `sqllineage/data/`
4. **Coverage**: Aim for 90%+ coverage, critical paths must be 100%
5. **Slow Tests**: Mark with `@pytest.mark.slow` if needed (currently not used)

### Performance Considerations

1. **Lazy Evaluation**: LineageRunner uses lazy evaluation - don't break this pattern
2. **Graph Operations**: NetworkX operations can be expensive on large graphs
3. **Parser Choice**: sqlfluff is more accurate but slower than sqlparse
4. **Statement Splitting**: Large SQL files with many statements can be slow

### Debugging Tips

1. **Enable Logging**: Set `SQLLINEAGE_LOG_LEVEL=DEBUG` environment variable
2. **AST Inspection**: Use sqlfluff CLI to inspect parse tree: `sqlfluff parse file.sql`
3. **Graph Visualization**: Use `to_cytoscape()` to visualize lineage graphs
4. **Metadata Issues**: Check `SQLLINEAGE_DEFAULT_SCHEMA` environment variable

## Useful Commands Reference

```bash
# Development
tox -e py310 --devenv venv           # Create dev environment
tox -e py310                         # Run all quality checks
pytest -v tests/sql/table/           # Run specific test directory
pytest -k "test_insert"              # Run tests matching pattern
pytest --cov --cov-report=html       # Generate HTML coverage report

# Code Quality
black .                              # Format all code
ruff check . --fix                   # Auto-fix linting issues
mypy                                 # Type check
pre-commit run --all-files           # Run all pre-commit hooks

# Frontend
cd sqllineagejs && npm start         # Start dev server
cd sqllineagejs && npm run build     # Build production assets
cd sqllineagejs && npm run lint      # Lint JavaScript

# CLI Usage
sqllineage --dialects                # List all supported dialects
sqllineage -e "SQL" --dialect=hive   # Parse with Hive dialect
sqllineage -f file.sql -l column -v  # Column lineage, verbose
sqllineage -g -H 0.0.0.0 -p 8080     # Visualization on custom host/port

# Git
git log --oneline -10                # View recent commits
git rebase -i master                 # Interactive rebase on master
```

## Resources

- **Documentation**: https://sqllineage.readthedocs.io
- **Demo**: https://reata.github.io/sqllineage/
- **Repository**: https://github.com/reata/sqllineage
- **Issues**: https://github.com/reata/sqllineage/issues
- **PyPI**: https://pypi.org/project/sqllineage/
- **Contributing Guide**: See CONTRIBUTING.md in repository root

---

**Last Updated**: 2025-11-17
**SQLLineage Version**: 1.5.6
**Python Versions**: 3.10, 3.11, 3.12, 3.13, 3.14
