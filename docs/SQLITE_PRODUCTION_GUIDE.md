# SQLite Production Guide

This guide explains how to use SQLite temporarily in production when PostgreSQL is not available.

## 🏗️ Architecture Overview

The application now uses a **unified repository pattern** that automatically handles database selection:

- **`unified_inquiry_repository`** - Routes chat inquiries to PostgreSQL or SQLite
- **`unified_user_repository`** - Routes user management to PostgreSQL or SQLite
- **Database files** are organized in the `database/` folder
- **Automatic fallback** from PostgreSQL to SQLite when needed

## 🎯 When to Use SQLite in Production

- **Temporary fallback** when PostgreSQL is down
- **Development/testing** environments
- **Small-scale deployments** with limited data
- **Emergency situations** requiring immediate deployment

## ⚠️ Important Considerations

### **Limitations:**
- **Concurrent writes**: SQLite has limited concurrent write performance
- **Scalability**: Not suitable for high-traffic applications
- **Backup**: Requires file-based backup strategy
- **Data integrity**: Less robust than PostgreSQL for complex operations

### **Recommended Usage:**
- **Short-term only** (days to weeks)
- **Low to medium traffic** (< 100 concurrent users)
- **Read-heavy workloads** (better for read operations)
- **Single server deployments**

## 📁 Database Structure

All SQLite databases are now organized in the `database/` folder:

```
database/
├── users.db                 # User management data
├── chat_inquiries.db       # Chat inquiry data  
├── collected_answers.db    # Answer storage data
└── migrations/             # Database migration scripts
```

## 🔧 Configuration for SQLite Production

### **1. Environment Variables**

```bash
# Force SQLite mode
ANSWER_STORAGE_TYPE=sqlite

# Database paths (all databases are now in the database/ folder)
SQLITE_DB_PATH=/var/lib/webchatbot/database/
SQLITE_USERS_DB=database/users.db
SQLITE_INQUIRIES_DB=database/chat_inquiries.db
SQLITE_ANSWERS_DB=database/collected_answers.db
```

### **2. Production Configuration**

```bash
# Production settings for SQLite
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_PERIOD=3600
```

## 🚀 Setup Steps

### **Step 1: Configure for SQLite**

```bash
# Set environment to force SQLite
export ANSWER_STORAGE_TYPE=sqlite

# Or update your .env file
echo "ANSWER_STORAGE_TYPE=sqlite" >> .env.production
```

### **Step 2: Setup SQLite Database**

```bash
# Run the unified user management script
python scripts/manage_users.py setup

# This will create in the database/ folder:
# - database/users.db (with default admin/test users)
# - database/chat_inquiries.db (for chat data)
# - database/collected_answers.db (for answer storage)
```

### **Step 3: Verify Setup**

```bash
# Test the setup
python -c "
from database.unified_user_repository import unified_user_repository
import asyncio
async def test():
    count = await unified_user_repository.get_user_count()
    print(f'Users in database: {count}')
asyncio.run(test())
"
```

## 📊 Default Users

The setup script creates these default users:

| Username | Password | Role | Email | User ID |
|----------|----------|------|-------|---------|
| `edifyho` | `Wildcat@007` | user | info@edify.in | e56b7839-29c6-44dd-bb38-5acb3433cdfb |
| `edifykids` | `Wildcat@007` | user | kids@edify.in | 25e9f8b2-268d-4fb2-8854-a893d9bafc43 |
| `drsis` | `Wildcat@007` | user | info@drsinternational.com | 6019ed7f-530d-463f-addd-a53f2e1ca3cc |
| `admin` | `Wildcat@007` | admin | support@jrcloudops.com | f484782b-1439-46c2-a752-f872d8e9b3ba |

**⚠️ IMPORTANT**: Change these passwords immediately in production!

## 🔄 Migration Strategy

### **From SQLite to PostgreSQL**

When PostgreSQL becomes available:

1. **Export SQLite data**:
   ```bash
   python scripts/export_sqlite_data.py
   ```

2. **Import to PostgreSQL**:
   ```bash
   python scripts/import_to_postgresql.py
   ```

3. **Switch configuration**:
   ```bash
   export ANSWER_STORAGE_TYPE=postgresql
   ```

### **Data Export Script**

```python
# scripts/export_sqlite_data.py
import sqlite3
import json
from datetime import datetime

def export_sqlite_data():
    """Export all SQLite data to JSON files"""
    
    # Export users
    with sqlite3.connect('database/users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        
        with open('users_export.json', 'w') as f:
            json.dump(users, f, indent=2, default=str)
    
    # Export chat inquiries
    with sqlite3.connect('database/chat_inquiries.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM chat_inquiry_information')
        inquiries = cursor.fetchall()
        
        with open('inquiries_export.json', 'w') as f:
            json.dump(inquiries, f, indent=2, default=str)
    
    print("✅ Data exported successfully!")

if __name__ == "__main__":
    export_sqlite_data()
```

## 🛡️ Security Considerations

### **1. File Permissions**
```bash
# Set proper permissions for SQLite files
chmod 600 *.db
chown webchatbot:webchatbot *.db
```

### **2. Backup Strategy**
```bash
# Create backup script
#!/bin/bash
# backup_sqlite.sh

BACKUP_DIR="/var/backups/webchatbot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp *.db $BACKUP_DIR/webchatbot_$DATE.db
gzip $BACKUP_DIR/webchatbot_$DATE.db

# Keep only last 7 days
find $BACKUP_DIR -name "webchatbot_*.db.gz" -mtime +7 -delete
```

### **3. Change Default Passwords**
```bash
# Update admin password
python -c "
from database.unified_user_repository import unified_user_repository
from models.user_models import UserUpdate
import asyncio

async def update_admin_password():
    admin_user = await unified_user_repository.get_user_by_username('admin')
    if admin_user:
        success = await unified_user_repository.update_user(admin_user.user_id, UserUpdate(password='YourNewSecurePassword123!'))
        if success:
            print('Admin password updated successfully!')
        else:
            print('Failed to update admin password!')
    else:
        print('Admin user not found!')

asyncio.run(update_admin_password())
"
```

## 📈 Performance Optimization

### **1. SQLite Configuration**
```python
# In your application startup
import sqlite3

def optimize_sqlite():
    """Optimize SQLite for production use"""
    # Optimize users database
    with sqlite3.connect('database/users.db') as conn:
        # Enable WAL mode for better concurrency
        conn.execute('PRAGMA journal_mode=WAL')
        
        # Increase cache size
        conn.execute('PRAGMA cache_size=10000')
        
        # Enable foreign keys
        conn.execute('PRAGMA foreign_keys=ON')
        
        # Optimize for performance
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA temp_store=MEMORY')
    
    # Optimize inquiries database
    with sqlite3.connect('database/chat_inquiries.db') as conn:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA cache_size=10000')
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA temp_store=MEMORY')
    
    # Optimize answers database
    with sqlite3.connect('database/collected_answers.db') as conn:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA cache_size=10000')
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA temp_store=MEMORY')
```

### **2. Connection Pooling**
```python
# Use connection pooling for better performance
import sqlite3
from contextlib import contextmanager

class SQLiteConnectionPool:
    def __init__(self, db_path, max_connections=10):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = []
    
    @contextmanager
    def get_connection(self):
        if self.connections:
            conn = self.connections.pop()
        else:
            conn = sqlite3.connect(self.db_path)
        
        try:
            yield conn
        finally:
            if len(self.connections) < self.max_connections:
                self.connections.append(conn)
            else:
                conn.close()
```

## 🔍 Monitoring

### **1. Database Size Monitoring**
```bash
# Monitor database size
watch -n 60 'ls -lh database/*.db'
```

### **2. Performance Monitoring**
```python
# Add to your application
import time
import sqlite3

def monitor_query_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        if end_time - start_time > 1.0:  # Log slow queries
            logger.warning(f"Slow query: {func.__name__} took {end_time - start_time:.2f}s")
        
        return result
    return wrapper
```

## 🚨 Emergency Procedures

### **If SQLite Database Gets Corrupted**

1. **Stop the application**
2. **Restore from backup**:
   ```bash
   cp /var/backups/webchatbot/webchatbot_latest.db.gz .
   gunzip webchatbot_latest.db.gz
   mv webchatbot_latest.db database/users.db
   ```
3. **Restart the application**

### **If Data is Lost**

1. **Check for WAL files**:
   ```bash
   ls -la database/*.db-wal database/*.db-shm
   ```
2. **Recover using WAL**:
   ```bash
   sqlite3 database/users.db "PRAGMA wal_checkpoint(FULL);"
   sqlite3 database/chat_inquiries.db "PRAGMA wal_checkpoint(FULL);"
   sqlite3 database/collected_answers.db "PRAGMA wal_checkpoint(FULL);"
   ```

## 📋 Checklist for SQLite Production

- [ ] ✅ Change default passwords
- [ ] ✅ Set proper file permissions
- [ ] ✅ Setup backup strategy
- [ ] ✅ Configure monitoring
- [ ] ✅ Test data export/import
- [ ] ✅ Plan migration to PostgreSQL
- [ ] ✅ Document emergency procedures
- [ ] ✅ Test failover scenarios

## 🎯 Best Practices

1. **Regular Backups**: Daily automated backups
2. **Monitor Performance**: Watch for slow queries
3. **Plan Migration**: Have PostgreSQL migration ready
4. **Test Regularly**: Verify data integrity
5. **Document Everything**: Keep track of all changes
6. **Security First**: Change all default credentials
7. **Monitor Resources**: Watch disk space and memory usage

## 🔄 Quick Commands

```bash
# Setup SQLite for production
export ANSWER_STORAGE_TYPE=sqlite
python scripts/manage_users.py setup

# Check database status
python -c "
from database.unified_user_repository import unified_user_repository
import asyncio
async def check():
    count = await unified_user_repository.get_user_count()
    print(f'Users: {count}')
asyncio.run(check())
"

# Backup databases
cp database/*.db /var/backups/webchatbot/

# Switch back to PostgreSQL
export ANSWER_STORAGE_TYPE=postgresql
```

Remember: **SQLite in production should be temporary only!** Always plan to migrate to PostgreSQL as soon as possible.
