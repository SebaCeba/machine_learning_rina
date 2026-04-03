# Machine Learning Rina - Project Guidelines

## Documentation-First Approach

**ALWAYS consult the `docs/` folder before making STRUCTURAL/ARCHITECTURAL decisions about:**
- Repository structure and organization
- Data folder layout and file naming
- Migration plans or refactoring proposals
- Architecture or component changes
- Adding new features or modules

**NOTE:** Minor code changes (bug fixes, function renaming, refactoring within existing structure) do NOT require consulting docs.

### Current Documentation Inventory

The `docs/` folder contains authoritative project documentation:

- **`docs/repo_state_audit.md`**: Complete inventory of current repository state, file purposes, and identified gaps. Use as baseline truth when analyzing what exists vs. what should exist.
- **`docs/data_folder_standard.md`**: Standardized data folder structure, naming conventions, governance rules, and migration plans. Reference before proposing data-related changes.

### Workflow

1. **Before structural/architectural changes**: Read relevant docs to understand current state
2. **Alert user immediately** if documentation is outdated or inconsistent with actual code
3. **If documentation doesn't exist**: Proceed with best practices and create documentation afterward
4. **After ANY code change**: Propose or create documentation updates in `docs/`
5. **When creating new documentation**: Follow the structure and style of existing docs
6. **When conflicts arise**: Documentation in `docs/` takes precedence over assumptions

## Project Context

This is a **refuge occupancy forecasting web application** built with:
- Flask 3.1.3 (web framework)
- Holt-Winters Exponential Smoothing via statsmodels (forecasting model)
- pandas for CSV parsing and time series processing
- 7-day seasonality, 30-day forecast horizon

**Key Characteristics:**
- Handles semicolon-delimited CSVs with Spanish characters
- Processes booking data (excluding cancellations: noches=0)
- Supports multiple date formats (DD-MM-YYYY, YYYY-MM-DD)
- Windows environment with batch automation (start.bat)

## Code Organization

```
app/
├── __init__.py      # Flask factory pattern
├── routes.py        # Upload and forecast endpoints
├── model.py         # Holt-Winters forecasting
└── data_loader.py   # CSV parsing and time series conversion

data/                # See docs/data_folder_standard.md for structure
templates/           # Single-page HTML UI
main.py              # Application entry point
```

## Standards

### Data Handling
- **Always** refer to `docs/data_folder_standard.md` for file organization
- Use lowercase with underscores for filenames
- Include timestamps for versioned data (YYYYMMDD format)
- Never modify raw historical data after upload

### CSV Processing
- Detect delimiters automatically (semicolon or comma)
- Use UTF-8-BOM encoding for Spanish characters
- Parse dates with `format='mixed', dayfirst=True`
- Exclude cancellations (noches=0) from analysis

### Documentation
- Keep docs concise and factual
- Use markdown tables for comparisons
- Include "Current State" vs "Target Structure" sections
- Provide migration checklists for implementation

## Git Workflow

Repository: `SebaCeba/machine_learning_rina`
- Track documentation in `docs/` (commit with descriptive messages)
- Exclude large data files via `.gitignore` (except reference samples)
- Test locally before pushing to main branch
