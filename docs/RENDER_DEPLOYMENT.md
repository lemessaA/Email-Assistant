# 🚀 Render.com Deployment Guide

## 📋 Overview

Render.com is a modern cloud platform that makes deploying web apps easy. This guide will help you deploy the Email Assistant with both API and UI services.

## 🏗️ Architecture

### Two Services Approach
1. **API Service** - FastAPI backend
2. **UI Service** - Streamlit frontend

### Service URLs
- **API**: `https://email-assistant-api.onrender.com`
- **UI**: `https://email-assistant-ui.onrender.com`

## 🚀 Quick Deploy

### Method 1: Using render.yaml (Recommended)

1. **Connect GitHub Repo**
   - Go to [render.com](https://render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Choose "Existing Dockerfile" or "Runtime: Python"

2. **Configure API Service**
   - Name: `email-assistant-api`
   - Runtime: Python 3.12
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

3. **Configure UI Service**
   - Name: `email-assistant-ui`
   - Runtime: Python 3.12
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run src/ui/streamlit_app.py --server.port $PORT --server.address 0.0.0.0`

### Method 2: Docker Deployment

1. **API Service**
   - Use `Dockerfile`
   - Port: 8000
   - Health Check: `/health`

2. **UI Service**
   - Use `Dockerfile.ui`
   - Port: 8501
   - Health Check: `/`

## 🔧 Environment Variables

### Required for API Service
```env
OPENAI_API_KEY=your_openai_key_here
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Required for UI Service
```env
API_URL=https://email-assistant-api.onrender.com
```

### Optional
```env
IMAP_SERVER=imap.gmail.com
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

## 📁 Files Created

- `render.yaml` - Render configuration file
- `Dockerfile` - API Docker configuration
- `Dockerfile.ui` - UI Docker configuration
- `RENDER_DEPLOYMENT.md` - This guide

## 🌐 Deployment URLs

After deployment:
- **API Health**: `https://email-assistant-api.onrender.com/health`
- **API Docs**: `https://email-assistant-api.onrender.com/docs`
- **Streamlit UI**: `https://email-assistant-ui.onrender.com`

## ⚡ Performance Tips

### Free Tier Limitations
- **Sleep after 15 minutes** of inactivity
- **Cold starts** may take 10-30 seconds
- **750 hours/month** limit

### Optimization
- Use webhooks to keep services awake
- Implement health checks
- Optimize startup time
- Use Redis for session storage

## 🔗 Connecting Services

### UI to API Connection
In Streamlit Cloud settings:
```python
# In streamlit_app.py
API_URL = os.environ.get("API_URL", "https://email-assistant-api.onrender.com")
```

### CORS Configuration
Ensure FastAPI allows UI origin:
```python
# In src/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://email-assistant-ui.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🐛 Troubleshooting

### Common Issues
1. **Port Binding**: Use `$PORT` environment variable
2. **CORS Errors**: Update CORS middleware settings
3. **Environment Variables**: Check Render dashboard
4. **Build Failures**: Verify requirements.txt
5. **Health Checks**: Ensure endpoints are accessible

### Debug Commands
```bash
# Check logs
render logs email-assistant-api

# Restart service
render restart email-assistant-api

# Check environment
render env email-assistant-api
```

## 📊 Monitoring

### Render Dashboard
- Service health status
- Resource usage metrics
- Error logs
- Deployment history

### Custom Monitoring
```python
# Add to your API
@app.get("/metrics")
def metrics():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

## 🎯 Production Tips

1. **Use Custom Domains**: Add your own domain
2. **SSL Certificates**: Auto-provided by Render
3. **Database**: Add PostgreSQL if needed
4. **Redis**: For caching and sessions
5. **Backups**: Enable automatic backups

## 🔄 CI/CD Integration

### Automatic Deployments
- Connect to GitHub
- Auto-deploy on push to main
- Preview deployments for PRs
- Rollback capabilities

### GitHub Actions (Optional)
```yaml
name: Deploy to Render
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        uses: johnnyhuy/render-deploy-action@v1
        with:
          service-url: ${{ secrets.RENDER_SERVICE_URL }}
          api-key: ${{ secrets.RENDER_API_KEY }}
```

## 📞 Support

- Render Docs: https://render.com/docs
- Status Page: https://status.render.com
- Support: support@render.com
- Community: https://community.render.com

## 🎉 Success!

Your Email Assistant is now running on Render with:
- ✅ FastAPI backend service
- ✅ Streamlit frontend service  
- ✅ Automatic HTTPS
- ✅ Custom domains support
- ✅ Free tier available
- ✅ Easy scaling options
