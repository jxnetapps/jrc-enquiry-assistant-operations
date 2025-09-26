# 🚀 SQLite Export API Documentation

This document provides comprehensive documentation for the SQLite to MongoDB Export API endpoints.

## 📋 **Overview**

The SQLite Export API provides endpoints to export data from SQLite to MongoDB when connectivity is restored. It includes background processing, progress tracking, and comprehensive error handling.

## 🔗 **Base URL**

```
http://localhost:8000/api/export
```

## 📊 **Available Endpoints**

### **1. Get SQLite Data Summary**

**Endpoint:** `GET /api/export/sqlite-data`

**Description:** Retrieves a summary of data available in SQLite without exporting.

**Response:**
```json
{
  "success": true,
  "message": "Found 29 records in SQLite",
  "data": {
    "total_records": 29,
    "sample_records": [
      {
        "id": "1",
        "user_id": null,
        "parentType": "New Parent",
        "schoolType": "Day School",
        "firstName": "John Doe",
        "mobile": "9876543210",
        "email": "john@example.com",
        "city": "New York",
        "childName": "Alice",
        "grade": "Grade 5",
        "academicYear": "2024-2025",
        "dateOfBirth": "2015-03-10",
        "schoolName": "Greenwood Academy",
        "status": "new",
        "source": "api",
        "created_at": "2023-10-27T10:00:00.000Z",
        "updated_at": "2023-10-27T10:00:00.000Z"
      }
    ],
    "statistics": {
      "unique_user_ids": 15,
      "parent_type_distribution": {
        "New Parent": 20,
        "Existing Parent": 9
      },
      "school_type_distribution": {
        "Day School": 18,
        "Boarding School": 11
      }
    }
  },
  "error": null
}
```

### **2. Test MongoDB Connection**

**Endpoint:** `POST /api/export/test-mongodb-connection`

**Description:** Tests MongoDB connectivity without exporting data.

**Response:**
```json
{
  "success": true,
  "message": "MongoDB connection successful",
  "data": {
    "connection_status": "connected",
    "database": "inquiryassistant",
    "collection": "chat_inquiry_information",
    "existing_records": 0
  },
  "error": null
}
```

### **3. Get Export Status**

**Endpoint:** `GET /api/export/status`

**Description:** Retrieves the current status of any running export operation.

**Response:**
```json
{
  "success": true,
  "message": "Export status retrieved successfully",
  "data": {
    "status": "idle",
    "total_records": 0,
    "processed_records": 0,
    "successful_records": 0,
    "failed_records": 0,
    "skipped_records": 0,
    "start_time": null,
    "end_time": null,
    "error_message": null
  },
  "error": null
}
```

**Status Values:**
- `idle`: No export operation is running
- `running`: Export operation is in progress
- `completed`: Export operation completed successfully
- `failed`: Export operation failed

### **4. Start Export**

**Endpoint:** `POST /api/export/sqlite-to-mongodb`

**Description:** Starts exporting data from SQLite to MongoDB in the background.

**Query Parameters:**
- `batch_size` (int, optional): Number of records to process in each batch (1-1000, default: 100)
- `skip_duplicates` (bool, optional): Whether to skip duplicate records (default: true)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/export/sqlite-to-mongodb?batch_size=50&skip_duplicates=true"
```

**Response:**
```json
{
  "success": true,
  "message": "Export started successfully",
  "data": {
    "export_id": "export_20240927_143022",
    "batch_size": 50,
    "skip_duplicates": true,
    "status": "started"
  },
  "error": null
}
```

### **5. Reset Export Status**

**Endpoint:** `POST /api/export/reset-export-status`

**Description:** Resets the export status (useful for clearing failed states).

**Response:**
```json
{
  "success": true,
  "message": "Export status reset successfully",
  "data": {
    "status": "idle",
    "total_records": 0,
    "processed_records": 0,
    "successful_records": 0,
    "failed_records": 0,
    "skipped_records": 0,
    "start_time": null,
    "end_time": null,
    "error_message": null
  },
  "error": null
}
```

## 🔄 **Export Process Flow**

### **Step 1: Check Data Availability**
```bash
curl -X GET "http://localhost:8000/api/export/sqlite-data"
```

### **Step 2: Test MongoDB Connection**
```bash
curl -X POST "http://localhost:8000/api/export/test-mongodb-connection"
```

### **Step 3: Start Export**
```bash
curl -X POST "http://localhost:8000/api/export/sqlite-to-mongodb?batch_size=100&skip_duplicates=true"
```

### **Step 4: Monitor Progress**
```bash
curl -X GET "http://localhost:8000/api/export/status"
```

## 📊 **Export Features**

### **Background Processing**
- Exports run in the background without blocking the API
- Multiple connection attempts with fallback methods
- Progress tracking and status updates

### **Duplicate Handling**
- Detects duplicates based on email and mobile number
- Option to skip or process duplicates
- Detailed statistics on skipped records

### **Error Handling**
- Graceful handling of connection failures
- Detailed error messages and logging
- Automatic retry mechanisms

### **Data Integrity**
- Preserves all original data fields
- Adds migration metadata for tracking
- Maintains data relationships and constraints

## 🛠️ **Usage Examples**

### **Basic Export**
```bash
# Start export with default settings
curl -X POST "http://localhost:8000/api/export/sqlite-to-mongodb"
```

### **Custom Batch Size**
```bash
# Export with smaller batch size for better monitoring
curl -X POST "http://localhost:8000/api/export/sqlite-to-mongodb?batch_size=25"
```

### **Include Duplicates**
```bash
# Export all records including duplicates
curl -X POST "http://localhost:8000/api/export/sqlite-to-mongodb?skip_duplicates=false"
```

### **Monitor Progress**
```bash
# Check export status
curl -X GET "http://localhost:8000/api/export/status"
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Export Not Starting**
- Check if another export is already running
- Verify MongoDB connectivity
- Reset export status if needed

#### **2. Connection Failures**
- The API automatically tries multiple connection methods
- Check MongoDB Atlas settings and network connectivity
- Verify connection string and credentials

#### **3. Data Validation Errors**
- Ensure SQLite data is properly formatted
- Check for required fields in records
- Verify data types and constraints

### **Error Responses**

#### **MongoDB Connection Failed**
```json
{
  "success": false,
  "message": "MongoDB connection test failed",
  "error": "SSL handshake failed: ..."
}
```

#### **Export Already Running**
```json
{
  "success": false,
  "message": "Export is already running",
  "error": "Another export operation is in progress"
}
```

#### **No Data Found**
```json
{
  "success": true,
  "message": "No data found in SQLite",
  "data": {
    "total_records": 0,
    "sample_records": []
  }
}
```

## 📈 **Performance Considerations**

### **Batch Size Optimization**
- **Small batches (25-50)**: Better for monitoring and error handling
- **Medium batches (100-200)**: Good balance of performance and monitoring
- **Large batches (500-1000)**: Faster processing but less granular monitoring

### **Memory Usage**
- Each batch is processed independently
- Memory usage scales with batch size
- Large datasets are processed incrementally

### **Network Considerations**
- Multiple connection attempts may increase latency
- Batch processing reduces network overhead
- Automatic retry mechanisms handle temporary failures

## 🔒 **Security Considerations**

### **Data Protection**
- All data is transmitted securely over HTTPS
- No sensitive data is logged in error messages
- Connection strings and credentials are protected

### **Access Control**
- API endpoints are publicly accessible (no authentication required)
- Consider adding authentication for production use
- Monitor access logs for suspicious activity

## 📝 **Migration Metadata**

Each exported record includes migration metadata:

```json
{
  "export_metadata": {
    "exported_at": "2024-09-27T14:30:22.123Z",
    "original_sqlite_id": "123",
    "export_version": "1.0"
  }
}
```

This metadata helps with:
- Tracking migration history
- Identifying source records
- Version control and rollback
- Data lineage and auditing

## 🎯 **Best Practices**

1. **Always test connection first** before starting export
2. **Use appropriate batch sizes** based on your data size
3. **Monitor progress regularly** during large exports
4. **Keep SQLite as backup** until migration is verified
5. **Test all functionality** after migration is complete

## 📞 **Support**

For issues or questions:
1. Check the export status endpoint for detailed error messages
2. Review application logs for additional context
3. Test MongoDB connectivity independently
4. Verify SQLite data integrity before export

---

**Note**: This API is designed to work seamlessly with the existing chat inquiry system and provides a robust solution for migrating data from SQLite to MongoDB when connectivity is restored.
