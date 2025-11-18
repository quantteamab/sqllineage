# Exact Commits from openmetadata-sqllineage Recommended for Upstream Contribution

## Summary

This document lists the exact commit hashes from openmetadata-sqllineage that should be contributed to the upstream reata/sqllineage project. All commits listed below are **NOT present** in reata/sqllineage v1.5.6.

---

## HIGH PRIORITY - Ready for Contribution

These commits provide clear value and should be contributed to upstream with minimal adaptation needed.

### 1. MSSQL-Specific Lineage Parsing Fix

**Commit Hash:** `7d44c97efee0b9d7f8be9b914aa7f7d9cc4cd285`
**Short Hash:** `7d44c97`
**Author:** Mayur Singal <39544459+ulixius9@users.noreply.github.com>
**Date:** 2023-08-17 15:34:56 +0530
**PR:** #19 (openmetadata)
**Subject:** Fix lineage parsing for mssql

**Files Changed:**
```
sqllineage/core/parser/sqlfluff/handlers/target.py |  2 +-
sqllineage/core/parser/sqlfluff/utils.py           |  6 +++++-
sqllineage/utils/helpers.py                        |  2 +-
tests/test_others_dialect_specific.py              | 17 +++++++++++++++++
```

**Why Contribute:**
- Fixes specific MSSQL dialect parsing issues
- Adds test coverage for MSSQL
- Small, focused change (4 files, 24 insertions, 3 deletions)
- Clear improvement for MSSQL users

**Adaptation Required:**
⚠️ MEDIUM - The `utils.py` file has diverged significantly between openmetadata and v1.5.6. The patch will need to be manually adapted to apply to the current structure.

**Command to Extract Patch:**
```bash
git format-patch -1 7d44c97efee0b9d7f8be9b914aa7f7d9cc4cd285
```

---

### 2. CREATE TABLE...CLONE and ALTER TABLE...SWAP Support

**Commit Hash:** `8882d4afa29a87e1bcef0b688d7035bcbbab4fd6`
**Short Hash:** `8882d4a`
**Author:** Mayur Singal <39544459+ulixius9@users.noreply.github.com>
**Date:** 2023-05-29 20:14:55 +0530
**PR:** #372 (openmetadata)
**Subject:** support create table..clone and alter table...swap

**Description:**
- Adds support for Snowflake `CREATE TABLE ... CLONE` syntax
- Adds support for `ALTER TABLE ... SWAP` operations
- Includes BigQuery test coverage

**Why Contribute:**
- Extends SQL dialect support for Snowflake operations
- Commonly used feature in cloud data warehouses
- Includes test coverage

**Adaptation Required:**
⚠️ LOW-MEDIUM - May conflict with reata's swap_partitions_between_tables refactoring (#616) which made it Vertica-only. Need to ensure both use cases are supported.

**Command to Extract Patch:**
```bash
git format-patch -1 8882d4afa29a87e1bcef0b688d7035bcbbab4fd6
```

---

## MEDIUM PRIORITY - Requires Review & Adaptation

These commits provide value but require more careful review and adaptation due to code divergence.

### 3. Complex Union Subqueries with CREATE VIEW Fix

**Commit Hash:** `61aee13f837849ba775fa0a7219e0e4fe88be8c5`
**Short Hash:** `61aee13`
**Author:** ulixius9 <mayursingal9@gmail.com>
**Date:** 2023-07-13 12:46:57 +0530
**Subject:** Fix complex union subqueries with create view

**Files Changed:**
```
sqllineage/core/parser/sqlfluff/utils.py | 12 ++++----
tests/test_columns.py                    | 49 ++++++++++++++++++++++++++++++++
```

**Why Contribute:**
- Handles complex UNION queries within CREATE VIEW statements
- Adds 49 comprehensive test cases
- Improves column-level lineage accuracy

**Adaptation Required:**
⚠️ HIGH - The utils.py file has significantly diverged. reata v1.5.6 already includes fix #726 for "nested UNION inside bracketed set_expression". Need to:
1. Compare the two approaches
2. Determine if openmetadata's fix covers additional edge cases
3. Extract test cases that aren't covered by v1.5.6
4. Potentially contribute just the missing test cases or combine approaches

**Recommendation:**
First analyze if reata v1.5.6's fix #726 covers the same scenarios. If not, extract the unique aspects and create a new patch.

**Command to Extract Patch:**
```bash
git format-patch -1 61aee13f837849ba775fa0a7219e0e4fe88be8c5
```

---

### 4. Enhanced Column-Level Lineage for INSERT & CREATE Queries

**Commit Hash:** `10bec6d1a40f2c68c826ddccd1a96d9853c41440`
**Short Hash:** `10bec6d`
**Author:** Mayur Singal <39544459+ulixius9@users.noreply.github.com>
**Co-Author:** reata <reddevil.hjw@gmail.com>
**Date:** 2023-06-11 17:08:45 +0530
**PR:** #371 (openmetadata)
**Subject:** feat: Improve column level lineage for insert & create queries (sqlfluff)

**Files Changed:**
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

**Full Commit Message:**
```
feat: Improve column level lineage for insert & create queries (sqlfluff) (#371)

* Improve column level lineage for insert & create queries
* fix format
* fix flake
* fix typing
* fix black
* fix type
* Address review comments: add target_column as property and add target columns as graph edge
* fix mypy: handle subquery type
* refactor: simplify SourceHandlerMixin logic
* refactor: simplify index store and query
* refactor: simplify DmlInsertExtractor
* test: move sqlfluff specific test cases to test_sqlfluff.py
* test: add a parenthesized union test case

Co-authored-by: reata <reddevil.hjw@gmail.com>
```

**Why Contribute:**
- Major improvement to column-level lineage for INSERT/CREATE
- 128 comprehensive test cases in test_sqlfluff.py
- Co-authored by reata (upstream maintainer), indicating it was reviewed
- Adds target_column as property
- Target columns as graph edges

**Adaptation Required:**
⚠️ HIGH - This is a large change (243 insertions, 75 deletions). reata v1.5.6 has since added:
- UPDATE statement column lineage (#524)
- Multiple source column lineage (#561)
- Different implementation approaches

Need to:
1. Compare implementation approaches
2. Identify unique improvements from openmetadata version
3. Extract valuable test cases
4. Determine if approaches can be merged or if one supersedes the other

**Recommendation:**
This requires careful analysis. Since reata was a co-author, he may have already incorporated these ideas differently in v1.5.6. Compare the two implementations and potentially contribute just the unique test cases or specific improvements.

**Command to Extract Patch:**
```bash
git format-patch -1 10bec6d1a40f2c68c826ddccd1a96d9853c41440
```

---

## FRONTEND IMPROVEMENTS - Optional but Valuable

These commits improve the user experience in the web UI.

### 5. Dialect Selection Persistence via localStorage

**Commit Hash:** `8ed0e5275f2dbef4801f6461fbfb7925d634907f`
**Short Hash:** `8ed0e52`
**Author:** reata <reddevil.hjw@gmail.com>
**Date:** 2023-06-11 20:17:57 +0800
**PR:** #388 (openmetadata)
**Subject:** fix: send lineage request with dialect from localStorage

**Why Contribute:**
- Improves UX by remembering user's dialect preference
- Authored by reata (upstream maintainer)
- Frontend-only change, low risk

**Adaptation Required:**
⚠️ LOW - Frontend code may have diverged, but concept is straightforward.

**Interesting Note:**
This was authored by reata himself but never made it into v1.5.6. This suggests it may have been deprioritized or replaced with a different approach.

**Command to Extract Patch:**
```bash
git format-patch -1 8ed0e5275f2dbef4801f6461fbfb7925d634907f
```

---

### 6. Click to Lock Highlighted Nodes

**Commit Hash:** `200c96f7674559c2b7adf05711dc1938d86513a2`
**Short Hash:** `200c96f`
**Author:** reata <reddevil.hjw@gmail.com>
**Date:** 2022-12-29 23:11:43 +0800
**PR:** #323 (openmetadata)
**Subject:** feat: click to lock highlighted nodes

**Why Contribute:**
- UX improvement for graph visualization
- Allows users to lock node selection
- Authored by reata (upstream maintainer)

**Adaptation Required:**
⚠️ LOW-MEDIUM - Frontend code may need adaptation.

**Command to Extract Patch:**
```bash
git format-patch -1 200c96f7674559c2b7adf05711dc1938d86513a2
```

---

### 7. Curved Lines in Graph Visualization

**Commit Hash:** `e940cbe9d301d8d0524b0e4ac4de6e653594bf41`
**Short Hash:** `e940cbe`
**Author:** reata <reddevil.hjw@gmail.com>
**Date:** 2022-12-22 18:52:23 +0800
**PR:** #321 (openmetadata)
**Subject:** feat: use curved lines in the graph

**Why Contribute:**
- Visual improvement to lineage graph
- Better aesthetics and clarity
- Authored by reata (upstream maintainer)

**Adaptation Required:**
⚠️ LOW-MEDIUM - Frontend code may need adaptation.

**Command to Extract Patch:**
```bash
git format-patch -1 e940cbe9d301d8d0524b0e4ac4de6e653594bf41
```

---

## LOWER PRIORITY - Potentially Already Fixed

These commits fix bugs that may already be addressed in v1.5.6 through different commits.

### 8. PostgreSQL Style Type Cast Support

**Commit Hash:** `c7be506430fb3d3bcbfc949d62fb16fd0ed6f757`
**Short Hash:** `c7be506`
**Author:** reata <reddevil.hjw@gmail.com>
**Date:** 2023-05-01 17:15:10 +0800
**PR:** #367 (openmetadata)
**Subject:** feat: support postgres style type cast

**Adaptation Required:**
⚠️ UNKNOWN - Need to verify if v1.5.6 already supports this syntax.

**Recommendation:**
Test if `::integer` style casting works in v1.5.6. If not, contribute this.

---

### 9. Parenthesis Around Arithmetic Operations Fix

**Commit Hash:** `c568aed460da3ec72443e57c806ea36781f8bf0e`
**Short Hash:** `c568aed`
**Author:** reata <reddevil.hjw@gmail.com>
**Date:** 2023-05-01 15:45:04 +0800
**PR:** #366 (openmetadata)
**Subject:** fix: parenthesis around arithmetic operation

**Adaptation Required:**
⚠️ UNKNOWN - Need to verify if v1.5.6 already handles this.

**Recommendation:**
Test if parenthesized arithmetic operations work correctly in v1.5.6. If not, contribute this.

---

### 10. Missing Column Lineage for SELECT DISTINCT Fix

**Commit Hash:** `6351f91b6e5bece7fab38a5ead8dd9f619284060`
**Short Hash:** `6351f91`
**Author:** reata <reddevil.hjw@gmail.com>
**Date:** 2023-05-01 15:11:08 +0800
**PR:** #365 (openmetadata)
**Subject:** fix: missing column lineage for select distinct

**Adaptation Required:**
⚠️ UNKNOWN - Need to verify if v1.5.6 already handles SELECT DISTINCT properly.

**Recommendation:**
Test if SELECT DISTINCT column lineage works correctly in v1.5.6. If not, contribute this.

---

## NOT RECOMMENDED for Contribution

### Initial SQLFluff Parser Integration

**Commit Hash:** `672e4fb6252e463e0fc371e629218e288f92da4f`
**Short Hash:** `672e4fb`
**Subject:** Add an option to use `sqlfluff` to be used as a query parser (#1)

**Why NOT Contribute:**
✅ Already present in v1.5.6 - reata/sqllineage already has full sqlfluff parser support

---

## Contribution Strategy & Priority Order

### Immediate Contribution (High Confidence):

1. **7d44c97** - MSSQL-specific lineage parsing fix
2. **8882d4a** - CREATE TABLE...CLONE support

### After Analysis & Testing:

3. **8ed0e52** - Dialect localStorage (if still desired by maintainer)
4. **200c96f** - Click to lock nodes (if UI direction aligns)
5. **e940cbe** - Curved lines (if UI direction aligns)

### After Detailed Comparison:

6. **61aee13** - Complex union fix (compare with v1.5.6's #726 first)
7. **10bec6d** - INSERT/CREATE lineage (compare with v1.5.6's approach first)

### After Verification:

8. **c7be506** - PostgreSQL type cast (test if needed)
9. **c568aed** - Parenthesis arithmetic (test if needed)
10. **6351f91** - SELECT DISTINCT (test if needed)

---

## How to Extract and Contribute

### Step 1: Create Patches
```bash
# For individual commits
git format-patch -1 <commit-hash>

# For multiple commits at once
git format-patch -1 7d44c97efee0b9d7f8be9b914aa7f7d9cc4cd285
git format-patch -1 8882d4afa29a87e1bcef0b688d7035bcbbab4fd6
```

### Step 2: Test Against v1.5.6
```bash
# Clone reata/sqllineage
git clone https://github.com/reata/sqllineage.git
cd sqllineage
git checkout v1.5.6

# Try applying the patch
git am < 0001-*.patch

# If it fails, manually adapt
git am --abort
# Manually port the changes
```

### Step 3: Create Pull Requests

For each commit:
1. Fork reata/sqllineage
2. Create feature branch from latest master (not v1.5.6)
3. Apply/adapt the patch
4. Ensure all tests pass
5. Add new tests if needed
6. Submit PR with clear description
7. Reference the original openmetadata PR

---

## Summary Table

| Priority | Commit | Subject | Adaptation | Value |
|----------|--------|---------|------------|-------|
| 🔴 HIGH | 7d44c97 | MSSQL fix | MEDIUM | High |
| 🔴 HIGH | 8882d4a | CLONE/SWAP | LOW-MED | High |
| 🟡 MED | 61aee13 | Union+VIEW | HIGH | Medium |
| 🟡 MED | 10bec6d | INSERT lineage | HIGH | High* |
| 🟡 MED | 8ed0e52 | localStorage | LOW | Medium |
| 🟢 LOW | 200c96f | Lock nodes | LOW-MED | Low |
| 🟢 LOW | e940cbe | Curved lines | LOW-MED | Low |
| 🟢 LOW | c7be506 | PG typecast | UNKNOWN | Low-Med |
| 🟢 LOW | c568aed | Parenthesis | UNKNOWN | Low |
| 🟢 LOW | 6351f91 | SELECT DISTINCT | UNKNOWN | Low |

\* High value but requires careful comparison with v1.5.6's implementation

---

## Important Notes

1. **Authored by reata:** Commits 8ed0e52, 200c96f, e940cbe, c7be506, c568aed, 6351f91 were all authored by reata (the upstream maintainer) but never made it into v1.5.6. This could mean:
   - They were experimental and later rejected
   - They were deprioritized
   - They were implemented differently in later versions
   - Consider discussing with reata before contributing these

2. **Co-authored commits:** Commit 10bec6d was co-authored by reata, suggesting he reviewed and approved the approach. Compare carefully with v1.5.6's implementation to see if ideas were incorporated differently.

3. **File structure differences:** openmetadata uses different directory structure for some files. When adapting patches, paths may need adjustment.

4. **Dependency versions:** openmetadata uses older sqlfluff (2.1.4) while v1.5.6 uses 3.4.2+. Some fixes may already be addressed by newer sqlfluff versions.

---

## Recommended First Steps

1. **Test v1.5.6** against your MSSQL use cases to confirm 7d44c97 is needed
2. **Compare** union handling between 61aee13 and v1.5.6's #726
3. **Compare** INSERT lineage between 10bec6d and v1.5.6's implementation
4. **Contact reata** to discuss which frontend features (200c96f, e940cbe, 8ed0e52) align with project direction
5. **Create patches** for 7d44c97 and 8882d4a as they have clear value

Good luck with the contributions!
