# Security Guide - GitHub Repository

## 🔒 What to Push and What NOT to Push

### ✅ SAFE to Push to GitHub

**Template Files (No Sensitive Data):**
- `config_template.env` ✅
- `config_template.env.development` ✅
- `config_template.env.production` ✅
- `config_template.env.azure` ✅

**Application Code:**
- All Python files (`.py`) ✅
- Documentation files (`.md`) ✅
- Scripts in `scripts/` folder ✅
- Requirements files ✅

### ❌ NEVER Push to GitHub (Sensitive Data)

**Environment Files (Contain Real Credentials):**
- `.env` ❌
- `.env.development` ❌
- `.env.production` ❌
- `.env.azure` ❌
- `.env.staging` ❌

**Database Files:**
- `*.db` ❌
- `*.sqlite3` ❌
- `chroma_db/` ❌

**Other Sensitive Files:**
- `*.log` ❌
- `__pycache__/` ❌

## 🛡️ How the System Protects You

### 1. `.gitignore` File
The `.gitignore` file automatically excludes sensitive files:

```gitignore
# Environment variables
.env
.env.local
.env.development
.env.staging
.env.production
.env.azure

# Database files
*.db
*.sqlite3
chroma_db/
```

### 2. Template-Based System
- **Templates** (safe to push) contain placeholder values
- **Actual .env files** (never pushed) contain real credentials
- **Generated from templates** using `python scripts/env-manager.py rebuild`

### 3. Environment-Specific Configuration
Each environment has its own file:
- Development → `.env.development` (local database)
- Production → `.env.production` (Supabase)
- Azure → `.env.azure` (Supabase)

## 🚨 Security Checklist

### Before Pushing to GitHub:

1. **Check git status:**
   ```bash
   git status
   ```

2. **Verify no .env files are tracked:**
   ```bash
   git status | findstr "\.env"
   # Should show no .env files (only config_template.env files)
   ```

3. **Check for sensitive data in templates:**
   ```bash
   findstr "password\|secret\|key" config_template.env*
   # Should only show placeholder values like "your_password_here"
   ```

### If You Accidentally Push Sensitive Data:

1. **Remove from git history:**
   ```bash
   git rm --cached .env
   git commit -m "Remove sensitive .env file"
   ```

2. **Update .gitignore:**
   ```bash
   echo ".env" >> .gitignore
   git add .gitignore
   git commit -m "Add .env to .gitignore"
   ```

3. **Force push (if necessary):**
   ```bash
   git push --force-with-lease
   ```

## 🔧 Safe Workflow

### 1. Initial Setup
```bash
# Clone repository
git clone <your-repo>

# Create environment files (not tracked by git)
python scripts/env-manager.py setup

# Add your real credentials to .env files (local only)
notepad .env.development
notepad .env.production
```

### 2. Making Changes
```bash
# Edit templates (safe to push)
notepad config_template.env.development

# Rebuild actual .env files (not tracked by git)
python scripts/env-manager.py rebuild

# Commit template changes
git add config_template.env.development
git commit -m "Update development template"
git push
```

### 3. Team Collaboration
```bash
# When team members pull changes
git pull

# They need to rebuild their .env files
python scripts/env-manager.py rebuild

# Then add their own credentials
notepad .env.development
```

## 📋 Template File Examples

### Safe Template (config_template.env.development):
```bash
# PostgreSQL Configuration
POSTGRESQL_CONNECTION_URI=postgresql://postgres:password@localhost:5432/database
POSTGRESQL_DATABASE_NAME=database_name
```

### Unsafe Actual File (.env.development):
```bash
# PostgreSQL Configuration
POSTGRESQL_CONNECTION_URI=postgresql://postgres:RealPassword123@localhost:5432/real_database
POSTGRESQL_DATABASE_NAME=real_database_name
```

## ⚠️ Important Notes

1. **Never commit actual .env files** - They contain real passwords and API keys
2. **Always use templates** - They contain safe placeholder values
3. **Check git status** before pushing - Make sure no sensitive files are tracked
4. **Use environment variables** in production - Don't rely on .env files
5. **Rotate credentials** if accidentally exposed

## 🎯 Summary

- **Templates** = Safe to push (placeholder values)
- **Actual .env files** = Never push (real credentials)
- **Git ignores** = Automatic protection
- **Team workflow** = Everyone rebuilds their own .env files
- **Security** = No sensitive data in repository
