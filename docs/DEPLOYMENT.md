# 🚀 Vercel Deployment Guide

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally
   ```bash
   npm install -g vercel
   ```
3. **GitHub Repo**: Push your code to GitHub

## 🔧 Environment Variables

Set these in your Vercel dashboard:

### Required
- `OPENAI_API_KEY`: Your OpenAI API key
- `SMTP_HOST`: Your SMTP server (e.g., smtp.gmail.com)
- `SMTP_USERNAME`: Your email username
- `SMTP_PASSWORD`: Your email password/app password

### Optional
- `IMAP_SERVER`: IMAP server (default: imap.gmail.com)
- `EMAIL_USER`: Email for IMAP
- `EMAIL_PASSWORD`: App password for IMAP

## 🚀 Quick Deploy

### Method 1: Using Script
```bash
./deploy.sh
```

### Method 2: Manual
```bash
# Install dependencies
pip install -r requirements-vercel.txt

# Deploy
vercel --prod
```

### Method 3: Vercel Dashboard
1. Connect your GitHub repo to Vercel
2. Set environment variables
3. Deploy automatically

## 🌐 Access Points

After deployment:
- **API**: `https://your-app.vercel.app/api/health`
- **UI**: You'll need Streamlit Cloud for the UI (see below)

## 🎨 UI Deployment (Streamlit Cloud)

Since Streamlit needs special handling:

1. **Create Streamlit Cloud Account**: [streamlit.io](https://streamlit.io)
2. **Connect GitHub Repo**
3. **Set Environment Variables**
4. **Deploy**

## 🔗 Connecting UI to API

In Streamlit Cloud, set:
- `API_URL`: `https://your-app.vercel.app`

## 📝 Notes

- Vercel handles the FastAPI backend
- Streamlit UI needs separate deployment
- Free tier limitations may apply
- Monitor usage and upgrade as needed

## 🐛 Troubleshooting

1. **Build Failures**: Check Python version compatibility
2. **Runtime Errors**: Verify environment variables
3. **CORS Issues**: Update CORS settings in `src/api/main.py`
4. **Timeouts**: Optimize API responses for serverless

## 📞 Support

- Vercel Docs: https://vercel.com/docs
- Streamlit Docs: https://docs.streamlit.io
- GitHub Issues: Create issue in repo
