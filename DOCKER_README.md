# 🐳 Docker Deployment Guide

This guide covers complete Docker deployment of the Email Assistant application with production-ready configuration.

## 📋 Prerequisites

- Docker & Docker Compose installed
- At least 4GB RAM available
- 10GB+ free disk space
- Git for cloning repository

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd Email-Assistant
```

### 2. Run Deployment Script
```bash
./docker-deploy.sh
```

This interactive script will:
- ✅ Create necessary directories
- ✅ Setup environment configuration
- ✅ Generate SSL certificates
- ✅ Pull Docker images
- ✅ Build custom images
- ✅ Start all services

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Port 80/443)              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Email Assistant API           │   │
│  │              (Port 8000)                │   │
│  │  ┌─────────────────────────────────────┐   │   │
│  │  │          Streamlit UI            │   │   │
│  │  │          (Port 8501)            │   │   │
│  │  └─────────────────────────────────────┘   │   │
│  │                                         │   │
│  │  ┌─────────────────────────────────────┐   │   │
│  │  │         Redis (Port 6379)       │   │   │
│  │  └─────────────────────────────────────┘   │   │
│  │                                         │   │
│  │  ┌─────────────────────────────────────┐   │   │
│  │  │        Ollama (Port 11434)       │   │   │
│  │  └─────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘
```

## 🛠️ Manual Deployment

### Environment Configuration
1. Copy `.env.production` to `.env`
2. Update with your actual credentials:
   ```bash
   # Email settings
   SMTP_USERNAME=your-email@company.com
   SMTP_PASSWORD=your-app-password
   
   # API keys
   SEARCH_API_KEY=your-search-api-key
   SECRET_KEY=your-super-secret-key
   ```

### Build and Start Services
```bash
# Build all services
docker-compose build

# Start core services
docker-compose up -d redis ollama

# Wait for Ollama, then download model
docker-compose exec ollama ollama pull llama2

# Start remaining services
docker-compose up -d email-assistant streamlit-ui nginx

# Optional: Start monitoring
docker-compose up -d prometheus grafana
```

## 📊 Service Access

| Service | URL | Credentials |
|---------|------|-------------|
| **Email Assistant API** | http://localhost:8000 | - |
| **Streamlit UI** | http://localhost:8501 | - |
| **Nginx (HTTPS)** | https://localhost | - |
| **Redis** | localhost:6379 | - |
| **Ollama** | http://localhost:11434 | - |
| **Grafana** | http://localhost:3000 | admin/admin123 |
| **Prometheus** | http://localhost:9090 | - |

## 🔧 Configuration Files

### Docker Compose Services

- **email-assistant**: Main FastAPI application
- **streamlit-ui**: Streamlit frontend
- **redis**: Caching layer
- **ollama**: Local LLM service
- **nginx**: Reverse proxy with SSL
- **prometheus**: Metrics collection
- **grafana**: Metrics visualization

### Environment Variables

Key variables in `.env`:
- `DATABASE_URL`: SQLite database path
- `SMTP_*`: Email server configuration
- `OLLAMA_BASE_URL`: LLM service URL
- `SEARCH_API_KEY`: Web search API key
- `SECRET_KEY`: Application secret

## 🔍 Monitoring & Logging

### Grafana Dashboards
- **API Performance**: Response times, error rates
- **Email Processing**: Throughput, success rates
- **Resource Usage**: CPU, memory, disk
- **LLM Metrics**: Model usage, response times

### Log Locations
- **Application logs**: `./logs/`
- **Nginx logs**: Container logs
- **Database logs**: SQLite file location

## 🔒 Security Features

- **Non-root users** in all containers
- **SSL/TLS encryption** via Nginx
- **Rate limiting** on API endpoints
- **Security headers** in Nginx config
- **Health checks** for all services

## 📈 Scaling Options

### Horizontal Scaling
```bash
# Scale API workers
docker-compose up -d --scale email-assistant=3

# Add load balancer
docker-compose -f docker-compose.scale.yml up -d
```

### Resource Limits
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

## 🛠️ Development Workflow

### Local Development
```bash
# Development mode with hot reload
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f email-assistant
```

### Production Deployment
```bash
# Production mode
docker-compose -f docker-compose.yml up -d

# Update services
docker-compose pull
docker-compose up -d --force-recreate
```

## 🔧 Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check logs
docker-compose logs [service-name]

# Check resource usage
docker stats

# Restart service
docker-compose restart [service-name]
```

**Ollama model not found:**
```bash
# Download model manually
docker-compose exec ollama ollama pull llama2

# Check available models
docker-compose exec ollama ollama list
```

**Database connection issues:**
```bash
# Check database file permissions
ls -la ./data/

# Recreate database
docker-compose exec email-assistant rm ./data/email_assistant.db
```

### Health Checks
```bash
# Check all services
docker-compose ps

# Test API health
curl http://localhost:8000/health

# Test UI health
curl http://localhost:8501/_stcore/health
```

## 🔄 Backup & Recovery

### Data Backup
```bash
# Backup application data
tar -czf backup-$(date +%Y%m%d).tar.gz ./data ./logs

# Backup Docker volumes
docker run --rm -v email-assistant_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz -C /data .
```

### Recovery
```bash
# Restore from backup
tar -xzf backup-20240101.tar.gz

# Restart services
docker-compose down
docker-compose up -d
```

## 📚 Advanced Configuration

### Custom Nginx Config
Edit `nginx/nginx.conf` for:
- Custom domains
- SSL certificate paths
- Advanced routing rules
- Additional security headers

### Prometheus Monitoring
Edit `monitoring/prometheus.yml` for:
- Custom metrics endpoints
- Alert rules
- Additional targets
- Retention policies

### Grafana Dashboards
Import custom dashboards:
1. Navigate to Grafana UI
2. Import JSON dashboard files
3. Configure data sources
4. Set up alerts

## 🚀 Production Deployment

### Cloud Deployment
```bash
# For cloud providers, modify docker-compose.yml:
# - Update environment variables
# - Configure cloud storage
# - Set up external databases
# - Configure load balancers

# Deploy to cloud
docker-compose -f docker-compose.cloud.yml up -d
```

### CI/CD Integration
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          docker-compose -f docker-compose.prod.yml up -d
```

## 📞 Support

For deployment issues:
1. Check this guide first
2. Review service logs
3. Verify environment configuration
4. Check resource availability

---

**🎉 Your Email Assistant is now containerized and production-ready!**
