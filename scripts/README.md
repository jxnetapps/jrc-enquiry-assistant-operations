# Scripts Directory

This directory contains utility scripts, test files, and supporting tools for the JRC Enquiry Assistant project.

## Organization

### Setup & Installation Scripts
- `setup-venv-robust.bat` - Robust virtual environment setup with enhanced error handling
- `setup-venv-troubleshoot.bat` - Diagnostic tool for Python installation issues
- `install-packages.bat` - Quick package installation script for virtual environment

### Startup Scripts (Alternative Modes)
- `start-sqlite.bat` / `start-sqlite.ps1` - Start application in SQLite-only mode
- `start-sqlite-only.ps1` - SQLite-only startup script
- `startup.sh` - Alternative startup script for Linux/Mac
- `start-dev.bat` / `start-dev.sh` - Development mode startup
- `start-prod.bat` / `start-prod.sh` - Production mode startup

### Test Scripts
- `test-app-startup.py` - Comprehensive startup test script
- `test-startup.py` - Basic startup test
- `test-sqlite-mode.py` - SQLite mode testing
- `test-postgresql-connection.py` - PostgreSQL connection testing

### Database & Migration Scripts
- `migrate.py` - Database migration script
- `migrate-production.py` - Production migration script
- `migrate_add_user_id.py` - Add user ID migration
- `migrate_users_to_database.py` - User migration script
- `setup_sqlite_users.py` - SQLite user setup

### Utility Scripts
- `manage_users.py` - User management utility
- `env-manager.py` - Environment variable manager
- `force-sqlite.ps1` / `force-sqlite.py` - Force SQLite mode
- `generate-azure-config.py` - Azure configuration generator

### Deployment Scripts
- `azure-deploy.ps1` / `azure-deploy.sh` - Azure deployment scripts
- `deploy-manual.ps1` - Manual deployment script

### Troubleshooting Scripts
- `quick-fix.ps1` - Quick fix utility
- `fix-postgresql-connection.ps1` - PostgreSQL connection fix
- `check-postgres.ps1` - PostgreSQL connection checker
- `cleanup-ports.ps1` - Port cleanup utility
- `setup-local-postgresql.ps1` - Local PostgreSQL setup

### Temporary Files
- `requirements_temp.txt` - Temporary requirements file (can be deleted)

## Usage

Most scripts can be run directly from the project root:

```bash
# Windows
scripts\test-app-startup.py
scripts\start-sqlite.bat

# Linux/Mac
./scripts/test-app-startup.py
./scripts/start-sqlite.sh
```

## Main Scripts (in Root Directory)

The following essential scripts remain in the root directory for easy access:
- `setup-venv.bat` / `setup-venv.sh` - Main virtual environment setup
- `start.bat` / `start.sh` - Main application startup
- `start-app.py` - Python application starter
- `install-windows.bat` - Main installation script

