# Troubleshooting Guide

This guide helps you resolve common issues with the JRC Enquiry Assistant Operations application.

## Common Issues and Solutions

### 1. Port 8000 Already in Use

**Error:** `[Errno 98] error while attempting to bind on address ('0.0.0.0', 8000): [errno 98] address already in use`

**Solution:**
1. Run the port cleanup script:
   ```powershell
   .\scripts\cleanup-ports.ps1
   ```

2. Or manually find and kill the process:
   ```powershell
   # Find processes using port 8000
   netstat -ano | findstr :8000
   
   # Kill the process (replace PID with actual process ID)
   taskkill /PID <PID> /F
   ```

3. Or change the port in your environment:
   ```powershell
   $env:PORT = "8001"
   python web_app.py
   ```

### 2. PostgreSQL Connection Failed

**Error:** `Failed to connect to PostgreSQL: Multiple exceptions`

**Solutions:**

1. **Check PostgreSQL Status:**
   ```powershell
   .\scripts\check-postgres.ps1
   ```

2. **Verify PostgreSQL is Running:**
   ```powershell
   # Check if PostgreSQL service is running
   Get-Service -Name "postgresql*"
   
   # Start PostgreSQL if not running
   Start-Service -Name "postgresql*"
   ```

3. **Check Connection String:**
   - Verify `POSTGRESQL_CONNECTION_URI` environment variable
   - Ensure the database exists
   - Check firewall settings

4. **Use SQLite Fallback:**
   - The application will automatically fall back to SQLite if PostgreSQL fails
   - This is normal behavior for development environments

### 3. FastAPI Deprecation Warnings

**Warning:** `on_event is deprecated, use lifespan event handlers instead`

**Solution:**
- This has been fixed in the latest version
- The application now uses modern FastAPI lifespan events
- No action required - warnings will disappear

### 4. Azure Deployment Issues

**Common Problems:**

1. **Startup Command Issues:**
   - Ensure `startup.sh` exists and is executable
   - Check that the startup script has proper permissions

2. **Environment Variables:**
   - Verify all required environment variables are set in Azure App Service
   - Check the configuration in Azure Portal

3. **Python Version:**
   - Ensure the correct Python version is specified
   - Current version: Python 3.13

### 5. Database Migration Issues

**If you encounter database migration errors:**

1. **Run migrations manually:**
   ```powershell
   python -m scripts.migrate
   ```

2. **Check database permissions:**
   - Ensure the database user has proper permissions
   - Verify connection string format

3. **Reset database (development only):**
   ```powershell
   # Delete SQLite files (WARNING: This will delete all data)
   Remove-Item "database\*.db" -Force
   python -m scripts.migrate
   ```

## Environment-Specific Issues

### Development Environment

1. **Missing Environment File:**
   - Create `.env.development` file
   - Copy from `config-templates/config_template.env.development`

2. **Python Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Database Setup:**
   ```powershell
   python -m scripts.migrate
   ```

### Production Environment

1. **Azure App Service Configuration:**
   - Check all environment variables in Azure Portal
   - Verify startup command is set correctly
   - Ensure proper Python version is selected

2. **PostgreSQL Configuration:**
   - Verify connection string format
   - Check firewall rules
   - Ensure database exists

## Logging and Debugging

### Enable Debug Logging

1. **Set environment variable:**
   ```powershell
   $env:DEBUG = "True"
   $env:LOG_LEVEL = "DEBUG"
   ```

2. **Check logs:**
   - Development: Logs appear in console
   - Production: Check Azure App Service logs

### Common Log Messages

- `PostgreSQL connection established` - Database connected successfully
- `Application will continue with SQLite fallback` - Using SQLite instead of PostgreSQL
- `Scheduler started` - Background tasks are running
- `Application startup complete` - Application is ready to serve requests

## Getting Help

If you continue to experience issues:

1. Check the logs for specific error messages
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed
4. Check network connectivity for database connections
5. Review the configuration files for any typos

## Quick Health Check

Run this command to check the overall health of your application:

```powershell
# Check if the application is running
curl http://localhost:8000/health

# Check Azure deployment
curl https://your-app-name.azurewebsites.net/health/azure
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "api": "running",
    "postgresql": "connected",
    "sqlite": "available"
  },
  "version": "2.0.0"
}
```
