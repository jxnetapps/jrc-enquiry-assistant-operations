# 🚀 Data Migration Guide: SQLite to MongoDB

This guide provides comprehensive instructions for migrating data from SQLite to MongoDB when connectivity is restored.

## 📋 **Prerequisites**

1. **MongoDB Connectivity**: Ensure MongoDB is accessible
2. **Backup**: Always backup your data before migration
3. **Python Environment**: Ensure all dependencies are installed

## 🛠️ **Migration Tools Available**

### 1. **Comprehensive Migration Tool** (`migrate_sqlite_to_mongodb.py`)
- Full-featured migration with verification
- Handles duplicates and errors gracefully
- Provides detailed logging and statistics
- Includes dry-run capability

### 2. **Quick Migration Tool** (`quick_migrate.py`)
- Simple, fast migration
- Minimal configuration required
- Good for small datasets

### 3. **Export/Import Utility** (`data_export_import.py`)
- Export data to JSON/CSV formats
- Import data from various sources
- Useful for backup and restore operations

## 🚀 **Migration Methods**

### **Method 1: Comprehensive Migration (Recommended)**

```bash
# Run the comprehensive migration tool
python migrate_sqlite_to_mongodb.py
```

**Features:**
- ✅ Multiple MongoDB connection attempts
- ✅ Duplicate detection and skipping
- ✅ Batch processing for large datasets
- ✅ Detailed progress reporting
- ✅ Migration verification
- ✅ Error handling and recovery

### **Method 2: Quick Migration**

```bash
# Run the quick migration tool
python quick_migrate.py
```

**Features:**
- ✅ Fast and simple
- ✅ Good for small to medium datasets
- ✅ Basic duplicate detection

### **Method 3: Export/Import Workflow**

```bash
# Run the export/import utility
python data_export_import.py
```

**Features:**
- ✅ Export to multiple formats (JSON, CSV)
- ✅ Import from various sources
- ✅ Interactive menu system
- ✅ Backup capabilities

## 📊 **Step-by-Step Migration Process**

### **Step 1: Pre-Migration Checklist**

1. **Verify MongoDB Connectivity**
   ```bash
   python -c "from database.mongodb_connection import mongodb_connection; import asyncio; asyncio.run(mongodb_connection.connect())"
   ```

2. **Backup Current Data**
   ```bash
   python data_export_import.py
   # Select option 1: Export SQLite to JSON
   ```

3. **Check Data Counts**
   ```bash
   python -c "
   import sqlite3
   conn = sqlite3.connect('chat_inquiries.db')
   cursor = conn.cursor()
   cursor.execute('SELECT COUNT(*) FROM chat_inquiry_information')
   print(f'SQLite records: {cursor.fetchone()[0]}')
   conn.close()
   "
   ```

### **Step 2: Perform Migration**

**Option A: Comprehensive Migration**
```bash
python migrate_sqlite_to_mongodb.py
```

**Option B: Quick Migration**
```bash
python quick_migrate.py
```

**Option C: Manual Export/Import**
```bash
python data_export_import.py
# Follow the interactive menu
```

### **Step 3: Verify Migration**

1. **Check Record Counts**
   ```bash
   python -c "
   from database.mongodb_connection import mongodb_connection
   import asyncio
   
   async def check():
       await mongodb_connection.connect()
       if mongodb_connection._client:
           db = mongodb_connection.get_database()
           collection = db['chat_inquiry_information']
           count = await collection.count_documents({})
           print(f'MongoDB records: {count}')
       else:
           print('MongoDB not connected')
   
   asyncio.run(check())
   "
   ```

2. **Test API Endpoints**
   ```bash
   # Test Simple API
   curl -X GET "http://localhost:8000/api/simple/chat-inquiry/stats"
   
   # Test Enhanced API
   curl -X GET "http://localhost:8000/api/v1/chat-inquiry/health"
   ```

### **Step 4: Post-Migration Tasks**

1. **Update Application Configuration**
   - Ensure MongoDB is set as primary database
   - Update connection settings if needed

2. **Test All Functionality**
   - Test all API endpoints
   - Verify user_id functionality
   - Check data integrity

3. **Monitor Performance**
   - Check response times
   - Monitor error logs
   - Verify data consistency

## 🔧 **Troubleshooting**

### **Common Issues and Solutions**

#### **Issue 1: MongoDB Connection Failed**
```
Error: SSL handshake failed
```
**Solution:**
- Check network connectivity
- Verify MongoDB Atlas settings
- Try different connection string
- Use the fallback methods in the migration tools

#### **Issue 2: Duplicate Records**
```
Warning: Skipping duplicate record
```
**Solution:**
- This is normal behavior
- Duplicates are detected by email or mobile
- Check if this is expected

#### **Issue 3: Validation Errors**
```
Error: Input should be a valid string
```
**Solution:**
- The migration tools handle ID conversion automatically
- Ensure you're using the latest version of the tools

#### **Issue 4: Large Dataset Performance**
```
Warning: Migration taking too long
```
**Solution:**
- Use batch processing (default: 100 records per batch)
- Increase batch size for better performance
- Monitor memory usage

## 📈 **Migration Statistics**

After successful migration, you should see:

```
📋 MIGRATION SUMMARY
==============================
✅ Migrated: X records
⏭️  Skipped: Y records (duplicates)
❌ Errors: Z records
📊 Final MongoDB count: Total records
```

## 🎯 **Best Practices**

1. **Always Backup First**
   - Export data to JSON/CSV before migration
   - Keep backup files in a safe location

2. **Test in Development**
   - Run migration on a copy of production data first
   - Verify all functionality works correctly

3. **Monitor During Migration**
   - Watch for errors and warnings
   - Check system resources (CPU, memory)

4. **Verify After Migration**
   - Compare record counts
   - Test API endpoints
   - Check data integrity

5. **Keep SQLite as Backup**
   - Don't delete SQLite database immediately
   - Keep it as a backup for a few days

## 🔄 **Rollback Plan**

If migration fails or issues are discovered:

1. **Stop the Application**
   ```bash
   # Stop the web application
   ```

2. **Restore from Backup**
   ```bash
   python data_export_import.py
   # Select option 4: Import JSON to SQLite
   ```

3. **Verify Data Integrity**
   ```bash
   python -c "
   import sqlite3
   conn = sqlite3.connect('chat_inquiries.db')
   cursor = conn.cursor()
   cursor.execute('SELECT COUNT(*) FROM chat_inquiry_information')
   print(f'SQLite records: {cursor.fetchone()[0]}')
   conn.close()
   "
   ```

4. **Restart Application**
   ```bash
   python web_app.py
   ```

## 📞 **Support**

If you encounter issues during migration:

1. Check the logs for detailed error messages
2. Verify MongoDB connectivity
3. Ensure all dependencies are installed
4. Try the different migration methods
5. Use the export/import utility for manual migration

## ✅ **Success Criteria**

Migration is successful when:

- ✅ All SQLite records are migrated to MongoDB
- ✅ No data loss during migration
- ✅ All API endpoints work correctly
- ✅ User ID functionality works
- ✅ Data integrity is maintained
- ✅ Application performance is acceptable

---

**Remember**: Always test the migration process in a development environment before running it on production data!
