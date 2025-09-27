# Database Migrations Guide

## Overview

This guide covers database schema migrations for the Web ChatBot application using PostgreSQL. The migration system ensures safe, versioned database schema changes across different environments.

## Migration System Features

- ✅ **Version Control**: Each migration has a unique timestamp-based version
- ✅ **Rollback Support**: Each migration includes a rollback script
- ✅ **Safety Checks**: Validation and backup procedures
- ✅ **Production Ready**: Includes backup and verification steps
- ✅ **Azure Integration**: Automated migration during deployment
- ✅ **CLI Tools**: Easy-to-use command-line interface

## Quick Start

### **1. Check Migration Status**
```bash
python scripts/migrate.py status
```

### **2. Run Migrations**
```bash
# Development/Staging
python scripts/migrate.py migrate

# Production (with backup)
python scripts/migrate-production.py
```

### **3. Create New Migration**
```bash
python scripts/migrate.py create --name add_user_preferences --description "Add user preferences table"
```

## Migration Commands

### **Basic Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `migrate` | Run all pending migrations | `python scripts/migrate.py migrate` |
| `status` | Show migration status | `python scripts/migrate.py status` |
| `create` | Create new migration | `python scripts/migrate.py create --name add_indexes` |
| `rollback` | Rollback specific migration | `python scripts/migrate.py rollback --version 20241227_000001` |

### **Advanced Options**

```bash
# Verbose logging
python scripts/migrate.py migrate --verbose

# Custom connection string
python scripts/migrate.py migrate --connection-string "postgresql://user:pass@host:port/db"

# Create migration with description
python scripts/migrate.py create --name add_audit_log --description "Add audit logging table"
```

## Migration Files Structure

```
database/migrations/
├── __init__.py
├── migration_manager.py
└── versions/
    ├── 20241227_000001_initial_schema.sql
    ├── 20241227_000001_initial_schema_rollback.sql
    ├── 20241227_000002_add_user_preferences.sql
    └── 20241227_000002_add_user_preferences_rollback.sql
```

### **Migration File Naming**
- Format: `YYYYMMDD_HHMMSS_description.sql`
- Rollback: `YYYYMMDD_HHMMSS_description_rollback.sql`
- Example: `20241227_000001_initial_schema.sql`

## Production Migration Process

### **1. Pre-Migration Checklist**

- [ ] **Backup Database**: Always create a backup before migration
- [ ] **Test in Staging**: Run migrations in staging environment first
- [ ] **Verify Connection**: Ensure database connectivity
- [ ] **Check Dependencies**: Verify all required packages are installed
- [ ] **Review Changes**: Review migration SQL for potential issues

### **2. Production Migration Steps**

```bash
# 1. Create backup (automatic in production script)
python scripts/migrate-production.py

# 2. Or manual backup
pg_dump -h host -U user -d database > backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Run migration
python scripts/migrate.py migrate --verbose

# 4. Verify migration
python scripts/migrate.py status
```

### **3. Rollback Process**

```bash
# Check applied migrations
python scripts/migrate.py status

# Rollback specific migration
python scripts/migrate.py rollback --version 20241227_000001_initial_schema

# Verify rollback
python scripts/migrate.py status
```

## Azure Deployment Integration

### **Automatic Migration During Deployment**

The Azure deployment scripts automatically run migrations:

```bash
# Windows
.\azure-deploy.ps1 -ResourceGroupName "webchatbot-rg" -WebAppName "webchatbot-app"

# Linux/Mac
./azure-deploy.sh -g webchatbot-rg -w webchatbot-app
```

### **Manual Migration in Azure**

```bash
# Connect to Azure App Service
az webapp ssh --resource-group webchatbot-rg --name webchatbot-app

# Run migration
cd /home/site/wwwroot
python scripts/migrate.py migrate

# Check status
python scripts/migrate.py status
```

## Docker Migration Support

### **Using Docker for Migrations**

```bash
# Build migration image
docker build -f docker/migrate.Dockerfile -t webchatbot-migrate .

# Run migrations
docker run --rm \
  -e POSTGRESQL_CONNECTION_URI="postgresql://user:pass@host:port/db" \
  webchatbot-migrate

# Check status
docker run --rm \
  -e POSTGRESQL_CONNECTION_URI="postgresql://user:pass@host:port/db" \
  webchatbot-migrate python scripts/migrate.py status
```

## Creating New Migrations

### **1. Create Migration File**

```bash
python scripts/migrate.py create --name add_audit_log --description "Add audit logging functionality"
```

This creates:
- `database/migrations/versions/20241227_120000_add_audit_log.sql`
- `database/migrations/versions/20241227_120000_add_audit_log_rollback.sql`

### **2. Write Migration SQL**

**Migration File (`20241227_120000_add_audit_log.sql`):**
```sql
-- Migration: 20241227_120000_add_audit_log
-- Description: Add audit logging functionality
-- Created: 2024-12-27T12:00:00Z

-- Create audit_log table
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
```

**Rollback File (`20241227_120000_add_audit_log_rollback.sql`):**
```sql
-- Rollback for migration: 20241227_120000_add_audit_log
-- Description: Remove audit logging functionality
-- Created: 2024-12-27T12:00:00Z

-- Drop indexes
DROP INDEX IF EXISTS idx_audit_log_created_at;
DROP INDEX IF EXISTS idx_audit_log_action;
DROP INDEX IF EXISTS idx_audit_log_user_id;

-- Drop table
DROP TABLE IF EXISTS audit_log;
```

### **3. Test Migration**

```bash
# Test migration
python scripts/migrate.py migrate

# Verify changes
python scripts/migrate.py status

# Test rollback
python scripts/migrate.py rollback --version 20241227_120000_add_audit_log

# Verify rollback
python scripts/migrate.py status
```

## Best Practices

### **1. Migration Design**

- **Atomic Changes**: Each migration should be atomic (all or nothing)
- **Backward Compatible**: Avoid breaking changes when possible
- **Test Rollbacks**: Always test rollback scripts
- **Document Changes**: Include clear descriptions and comments

### **2. Production Safety**

- **Always Backup**: Create database backup before migration
- **Test First**: Run migrations in staging environment
- **Monitor Performance**: Watch for performance impact
- **Have Rollback Plan**: Know how to rollback if issues occur

### **3. Schema Changes**

- **Add Columns**: Use `ALTER TABLE ADD COLUMN` with defaults
- **Drop Columns**: Use `ALTER TABLE DROP COLUMN` carefully
- **Index Changes**: Add indexes in separate migration
- **Data Migrations**: Use separate migration for data changes

### **4. Performance Considerations**

- **Large Tables**: Use `CREATE INDEX CONCURRENTLY` for large tables
- **Batch Operations**: Process large data changes in batches
- **Off-Peak Hours**: Run migrations during low-traffic periods
- **Monitor Locks**: Watch for table locks during migration

## Troubleshooting

### **Common Issues**

#### **1. Migration Fails**
```bash
# Check error logs
python scripts/migrate.py migrate --verbose

# Check database connection
python -c "from config import Config; print(Config.POSTGRESQL_CONNECTION_URI)"
```

#### **2. Rollback Fails**
```bash
# Check if rollback file exists
ls database/migrations/versions/*_rollback.sql

# Manual rollback
psql -h host -U user -d database -f migration_rollback.sql
```

#### **3. Connection Issues**
```bash
# Test connection
psql -h host -U user -d database -c "SELECT 1"

# Check environment variables
python -c "from config import Config; print(Config.POSTGRESQL_CONNECTION_URI)"
```

### **Debug Commands**

```bash
# Enable debug logging
export PYTHONPATH=/app
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from database.migrations.migration_manager import MigrationManager
manager = MigrationManager()
print(manager.status())
"
```

## Monitoring and Alerts

### **1. Migration Status Monitoring**

```bash
# Check migration status
python scripts/migrate.py status

# Monitor migration logs
tail -f migration.log
```

### **2. Database Health Checks**

```sql
-- Check migration table
SELECT * FROM schema_migrations ORDER BY applied_at DESC;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### **3. Performance Monitoring**

```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check table statistics
SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
FROM pg_stat_user_tables
ORDER BY n_tup_ins DESC;
```

## Security Considerations

### **1. Access Control**

- **Limited Permissions**: Use dedicated migration user with limited permissions
- **Environment Separation**: Use different credentials for each environment
- **Audit Trail**: Log all migration activities

### **2. Sensitive Data**

- **No Secrets in Migrations**: Never include passwords or API keys
- **Data Masking**: Mask sensitive data in test environments
- **Encryption**: Use encrypted connections for production

### **3. Backup Security**

- **Encrypted Backups**: Encrypt database backups
- **Secure Storage**: Store backups in secure location
- **Access Control**: Limit access to backup files

## Summary

The migration system provides:

- ✅ **Safe Schema Changes**: Versioned, rollback-capable migrations
- ✅ **Production Ready**: Backup and verification procedures
- ✅ **Easy to Use**: Simple CLI commands
- ✅ **Azure Integrated**: Automatic migration during deployment
- ✅ **Docker Support**: Containerized migration execution
- ✅ **Comprehensive Documentation**: Complete usage guide

This ensures your database schema can be safely updated across all environments! 🎉
