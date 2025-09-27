# Environment Management Guide

This guide explains how to manage different environments (development, staging, production) for the Web ChatBot application.

## Overview

The application supports three environments:
- **Development**: Local development with relaxed settings
- **Staging**: Pre-production testing environment
- **Production**: Live production environment

## Quick Start

### 1. Setup Environment

```bash
# Setup development environment
python scripts/setup-env.py development

# Setup staging environment
python scripts/setup-env.py staging

# Setup production environment
python scripts/setup-env.py production
```

### 2. Run Application

#### Windows:
```bash
# Development
scripts\start-dev.bat

# Staging
scripts\start-staging.bat

# Production
scripts\start-prod.bat
```

#### Linux/Mac:
```bash
# Development
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh

# Staging
chmod +x scripts/start-staging.sh
./scripts/start-staging.sh

# Production
chmod +x scripts/start-prod.sh
./scripts/start-prod.sh
```

#### Manual:
```bash
# Development
ENVIRONMENT=development python web_app.py

# Staging
ENVIRONMENT=staging python web_app.py

# Production
ENVIRONMENT=production python web_app.py
```

## Environment Configuration Files

| Environment | Config File | Description |
|-------------|-------------|-------------|
| Development | `.env.development` | Local development settings |
| Staging | `.env.staging` | Pre-production testing |
| Production | `.env.production` | Live production settings |

## Environment-Specific Settings

### Development
- **Debug**: Enabled
- **Logging**: DEBUG level
- **Rate Limiting**: Disabled
- **Database**: Local FAISS
- **Crawling**: Limited (10 pages, depth 2)
- **Auth**: Allow any user enabled

### Staging
- **Debug**: Disabled
- **Logging**: INFO level
- **Rate Limiting**: Moderate (200 req/hour)
- **Database**: Local FAISS
- **Crawling**: Moderate (100 pages, depth 3)
- **Auth**: Standard authentication

### Production
- **Debug**: Disabled
- **Logging**: INFO level
- **Rate Limiting**: Strict (100 req/hour)
- **Database**: Chroma Cloud
- **Crawling**: Full (500 pages, depth 5)
- **Auth**: Strict authentication

## Docker Support

### Using Docker Compose

```bash
# Start development environment
docker-compose up webchatbot-dev

# Start staging environment
docker-compose up webchatbot-staging

# Start production environment
docker-compose up webchatbot-prod
```

### Using Docker

```bash
# Build image
docker build -t webchatbot .

# Run development
docker run -e ENVIRONMENT=development --env-file .env.development -p 8000:8000 webchatbot

# Run staging
docker run -e ENVIRONMENT=staging --env-file .env.staging -p 8001:8000 webchatbot

# Run production
docker run -e ENVIRONMENT=production --env-file .env.production -p 8002:8000 webchatbot
```

## Environment Variables

### Required for All Environments
- `ENVIRONMENT`: Environment name (development/staging/production)
- `JWT_SECRET_KEY`: JWT signing key
- `POSTGRESQL_CONNECTION_URI`: Database connection string

### Development Specific
- `DEBUG=true`: Enable debug mode
- `LOG_LEVEL=DEBUG`: Verbose logging
- `ALLOW_ANY_USER=true`: Allow any user login

### Production Specific
- `OPENAI_API_KEY`: OpenAI API key
- `CHROMA_CLOUD_API_KEY`: Chroma Cloud API key
- `CHROMA_CLOUD_TENANT_ID`: Chroma Cloud tenant ID
- `CHROMA_CLOUD_DATABASE_ID`: Chroma Cloud database ID

## Security Considerations

### Development
- Use weak passwords for testing
- Enable debug mode
- Allow any user authentication
- Disable rate limiting

### Staging
- Use moderate security settings
- Test with production-like configuration
- Enable rate limiting
- Use staging API keys

### Production
- Use strong, unique passwords
- Disable debug mode
- Use production API keys
- Enable strict rate limiting
- Use HTTPS/SSL certificates

## Deployment Checklist

### Before Production Deployment

1. **Environment Setup**
   - [ ] Copy `config_template.env.production` to `.env.production`
   - [ ] Update all production-specific values
   - [ ] Test configuration with staging environment

2. **Security**
   - [ ] Change default passwords
   - [ ] Generate strong JWT secret
   - [ ] Configure production API keys
   - [ ] Enable rate limiting
   - [ ] Disable debug mode

3. **Database**
   - [ ] Setup production PostgreSQL database
   - [ ] Configure Chroma Cloud (if using)
   - [ ] Test database connections

4. **Monitoring**
   - [ ] Configure logging
   - [ ] Setup monitoring/alerting
   - [ ] Test error handling

## Troubleshooting

### Common Issues

1. **Environment not loading**
   - Check if `.env.{environment}` file exists
   - Verify `ENVIRONMENT` variable is set correctly

2. **Database connection failed**
   - Verify `POSTGRESQL_CONNECTION_URI` is correct
   - Check database server is running
   - Verify credentials

3. **API keys not working**
   - Check if API keys are set in environment file
   - Verify API keys are valid and have proper permissions

4. **Rate limiting issues**
   - Check `RATE_LIMIT_ENABLED` setting
   - Adjust `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_PERIOD`

### Debug Commands

```bash
# Check current environment
echo $ENVIRONMENT

# Test configuration loading
python -c "from config import Config; print(f'Environment: {Config.ENVIRONMENT}')"

# Validate environment file
python -c "from dotenv import load_dotenv; load_dotenv('.env.production'); print('Production config loaded')"
```

## Best Practices

1. **Never commit `.env` files** to version control
2. **Use different databases** for each environment
3. **Test configuration changes** in staging before production
4. **Monitor logs** in production environment
5. **Keep secrets secure** and rotate regularly
6. **Use environment-specific API keys** when possible
