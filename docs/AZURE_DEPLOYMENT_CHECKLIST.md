# Azure Deployment Checklist

## Pre-Deployment

### ✅ Prerequisites
- [ ] Azure subscription active
- [ ] Azure CLI installed and logged in
- [ ] GitHub repository with code
- [ ] Required API keys and credentials ready

### ✅ Environment Setup
- [ ] Create `.env.production` from template
- [ ] Update all production-specific values
- [ ] Test configuration locally
- [ ] Create deployment package

## Deployment

### ✅ Resource Creation
- [ ] Create resource group
- [ ] Create App Service plan
- [ ] Create web app
- [ ] Create PostgreSQL database (if needed)
- [ ] Create Application Insights (optional)

### ✅ Configuration
- [ ] Set environment variables
- [ ] Configure startup command
- [ ] Set up custom domain (if needed)
- [ ] Configure SSL certificate
- [ ] Set up monitoring

### ✅ Code Deployment
- [ ] Deploy application code
- [ ] Verify deployment success
- [ ] Test application endpoints
- [ ] Check application logs

## Post-Deployment

### ✅ Testing
- [ ] Test API endpoints
- [ ] Test authentication
- [ ] Test database connections
- [ ] Test external API calls
- [ ] Performance testing

### ✅ Security
- [ ] Verify HTTPS is enabled
- [ ] Check environment variables are secure
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts

### ✅ Monitoring
- [ ] Application Insights configured
- [ ] Log analytics set up
- [ ] Performance monitoring active
- [ ] Error tracking enabled

## Maintenance

### ✅ Regular Tasks
- [ ] Monitor application performance
- [ ] Check error logs
- [ ] Update dependencies
- [ ] Backup database
- [ ] Review costs

### ✅ Security Updates
- [ ] Update Python packages
- [ ] Update Azure resources
- [ ] Rotate secrets
- [ ] Security scans

## Quick Commands

```bash
# Check deployment status
az webapp show --name webchatbot-app --resource-group webchatbot-rg

# View logs
az webapp log tail --name webchatbot-app --resource-group webchatbot-rg

# Restart app
az webapp restart --name webchatbot-app --resource-group webchatbot-rg

# Update app settings
az webapp config appsettings set --name webchatbot-app --resource-group webchatbot-rg --settings KEY=VALUE
```
