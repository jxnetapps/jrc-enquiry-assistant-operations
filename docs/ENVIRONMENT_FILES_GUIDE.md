# Environment Files Guide

## Overview

This project uses a **single robust method** for managing environment configurations. No confusion, no multiple options - just one clear way to do things.

## The One Method: Template-Based Approach

**Rule**: Edit templates → Rebuild → Done!

## File Structure

```
project/
├── config-templates/config_template.env.development  # Development template (EDIT THIS)
├── config-templates/config_template.env.production   # Production template (EDIT THIS)
├── config-templates/config_template.env.azure        # Azure template (EDIT THIS)
├── .env.development                # Generated from template
├── .env.production                 # Generated from template
├── .env.azure                      # Generated from template
└── .env                            # Generated from template
```

## How It Works

### 1. Environment Detection
```python
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # Defaults to "development"
```

### 2. File Loading
1. Look for `.env.{ENVIRONMENT}` (e.g., `.env.development`)
2. Fallback to `.env` if not found

### 3. Database Configuration

| Environment | Template File | Database Used |
|-------------|---------------|---------------|
| Development | `config-templates/config_template.env.development` | Local PostgreSQL |
| Production | `config-templates/config_template.env.production` | Supabase |
| Azure | `config-templates/config_template.env.azure` | Supabase |

## The One Method: How to Change Settings

### Step 1: Edit Template Files
```bash
# Edit the template file for your environment
notepad config-templates/config_template.env.development
notepad config-templates/config_template.env.production
```

### Step 2: Rebuild Environment Files
```bash
python scripts/env-manager.py rebuild
```

### Step 3: Start Application
```bash
# Development (uses .env.development automatically)
scripts/start-dev.bat    # Windows
scripts/start-dev.sh     # Linux/Mac

# Production (uses .env.production automatically)
scripts/start-prod.bat   # Windows
scripts/start-prod.sh    # Linux/Mac
```

## Quick Commands

```bash
# Initial setup (first time only)
python scripts/env-manager.py setup

# Show current configuration
python scripts/env-manager.py show

# Rebuild all .env files from templates
python scripts/env-manager.py rebuild

# Start application
scripts/start-dev.bat     # Development (Windows)
scripts/start-prod.bat    # Production (Windows)
scripts/start-dev.sh      # Development (Linux/Mac)
scripts/start-prod.sh     # Production (Linux/Mac)

# Test database connectivity
python tests/test_postgres_health.py
```

## What to Edit

### For Development Changes:
- **File**: `config-templates/config_template.env.development`
- **Key Setting**: `POSTGRESQL_CONNECTION_URI` (for local PostgreSQL)

### For Production Changes:
- **File**: `config-templates/config_template.env.production`
- **Key Setting**: `POSTGRESQL_CONNECTION_URI` (for Supabase)

## Example: Switch Development to Use Supabase

1. **Edit template**:
   ```bash
   notepad config-templates/config_template.env.development
   # Change: POSTGRESQL_CONNECTION_URI=postgresql://postgres:password@localhost:5432/jrc_chatbot_assistant_dev
   # To:     POSTGRESQL_CONNECTION_URI=postgresql://postgres:password@db.umwxkbcvqvqqybjwcash.supabase.co:5432/postgres
   ```

2. **Rebuild**:
   ```bash
   python scripts/env-manager.py rebuild
   ```

3. **Start application**:
   ```bash
   scripts/start-dev.bat    # Windows
   scripts/start-prod.bat   # Windows
   scripts/start-dev.sh     # Linux/Mac
   scripts/start-prod.sh    # Linux/Mac
   ```

## Health Check Endpoints

```bash
# General health
curl http://localhost:8000/api/chat-inquiry/health

# Database status
curl http://localhost:8000/api/chat-inquiry/database/status

# Detailed PostgreSQL health
curl http://localhost:8000/api/chat-inquiry/database/postgres-health
```

## Summary

- **Templates** = Source files (version controlled) - **EDIT THESE**
- **Environment files** = Generated files (not version controlled) - **DON'T EDIT THESE**
- **One method**: Edit templates → Rebuild → Restart
- **No confusion**: Only one way to do things
