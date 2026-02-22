# 🔍 Web Search Integration Setup Guide

This guide covers setting up multiple web search engines for your Email Assistant.

## 🚀 Supported Search Engines

### 1. **Serper API** (Recommended for General Search)
- **Provider**: Google Search Results
- **Cost**: $5/month for 5,000 searches
- **Best for**: General web searches, fast results
- **Setup**: Easy, minimal configuration

### 2. **Tavily AI** (Recommended for AI Context)
- **Provider**: AI-optimized search
- **Cost**: $5/month for 1,000 searches
- **Best for**: Email context understanding, AI responses
- **Setup**: Easy, includes AI-generated answers

### 3. **Google Custom Search API**
- **Provider**: Official Google API
- **Cost**: $5 per 1,000 searches
- **Best for**: Enterprise, custom domains
- **Setup**: Complex, requires Custom Search Engine

### 4. **Bing Search API**
- **Provider**: Microsoft Bing
- **Cost**: $7/month for 3,000 searches
- **Best for**: Alternative results, news search
- **Setup**: Medium complexity

## 🛠️ Setup Instructions

### Option 1: Serper API (Recommended Primary)

1. **Sign up for Serper**:
   - Go to [serper.dev](https://serper.dev)
   - Create account and get API key
   - Free tier: 2,000 searches/month

2. **Configure Environment**:
   ```bash
   # Add to .env file
   SERPER_API_KEY=your-serper-api-key
   ```

3. **Test Integration**:
   ```python
   from src.integrations.web_search import WebSearchIntegration
   
   search = WebSearchIntegration()
   results = search.search("Python programming", engine="serper")
   print(results)
   ```

### Option 2: Tavily AI (Recommended for AI Context)

1. **Sign up for Tavily**:
   - Go to [tavily.com](https://tavily.com)
   - Create account and get API key
   - Free tier: 1,000 searches/month

2. **Configure Environment**:
   ```bash
   # Add to .env file
   TAVILY_API_KEY=your-tavily-api-key
   ```

3. **Test AI-Optimized Search**:
   ```python
   search = WebSearchIntegration()
   results = search.search("email automation", search_type="ai_context")
   print(results)
   ```

### Option 3: Google Custom Search API

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable "Custom Search API"
   - Create API key

2. **Create Custom Search Engine**:
   - Go to [cse.google.com](https://cse.google.com)
   - Create search engine
   - Get "Search engine ID" (CX)

3. **Configure Environment**:
   ```bash
   # Add to .env file
   GOOGLE_SEARCH_API_KEY=your-google-api-key
   GOOGLE_SEARCH_CX=your-custom-search-id
   ```

### Option 4: Bing Search API

1. **Create Azure Account**:
   - Go to [Azure Portal](https://portal.azure.com/)
   - Create "Bing Search v7" resource
   - Get API key

2. **Configure Environment**:
   ```bash
   # Add to .env file
   BING_SEARCH_API_KEY=your-bing-api-key
   ```

## 🎯 Recommended Configuration

### **Best Setup: Serper + Tavily**

```bash
# .env file
SERPER_API_KEY=your-serper-key
TAVILY_API_KEY=your-tavily-key
```

**Why this combo:**
- **Serper**: Fast, reliable general searches
- **Tavily**: AI-optimized for email context
- **Smart routing**: Auto-selects best engine per use case

### **Budget-Friendly Setup: Serper Only**

```bash
# .env file
SERPER_API_KEY=your-serper-key
```

### **Enterprise Setup: All Engines**

```bash
# .env file
SERPER_API_KEY=your-serper-key
TAVILY_API_KEY=your-tavily-key
GOOGLE_SEARCH_API_KEY=your-google-key
GOOGLE_SEARCH_CX=your-google-cx
BING_SEARCH_API_KEY=your-bing-key
```

## 🔧 Usage Examples

### **General Web Search**
```python
search_tools.web_search(
    query="Python email automation",
    max_results=5,
    engine="auto"  # Auto-selects best engine
)
```

### **AI Context Search** (Perfect for Email Assistant)
```python
search_tools.ai_context_search(
    query="professional email writing best practices",
    max_results=3
)
```

### **News Search**
```python
search_tools.news_search(
    query="AI email assistant news",
    max_results=5
)
```

### **Academic Search**
```python
search_tools.academic_search(
    query="machine learning email classification",
    max_results=5
)
```

### **Engine-Specific Search**
```python
# Force specific engine
search_tools.web_search(
    query="email marketing",
    engine="tavily",  # or "serper", "google", "bing"
    search_type="general"
)
```

## 📊 Search Engine Comparison

| Feature | Serper | Tavily AI | Google API | Bing API |
|----------|---------|------------|------------|-----------|
| **Speed** | ⚡ Fast | 🚀 Fast | ⚡ Fast | ⚡ Fast |
| **AI Context** | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **News Focus** | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **Academic** | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **Cost** | 💰 Low | 💰 Low | 💸 High | 💰 Medium |
| **Setup** | ✅ Easy | ✅ Easy | ❌ Complex | ⚠️ Medium |
| **Reliability** | ✅ High | ✅ High | ✅ High | ✅ High |

## 🔄 Smart Search Routing

The system automatically selects the best engine based on search type:

### **General Search** → Serper
- Fast, reliable results
- Good coverage
- Cost-effective

### **AI Context Search** → Tavily
- AI-optimized results
- Includes AI-generated answers
- Perfect for email understanding

### **News Search** → Bing
- Strong news coverage
- Recent results
- Good for current events

### **Academic Search** → Tavily
- Academic domain filtering
- Research-focused results
- Good for technical queries

## 🛡️ Error Handling & Fallbacks

### **Automatic Fallbacks**
1. **Primary engine fails** → Try secondary engine
2. **All engines fail** → Return mock results
3. **API key missing** → Use available engines
4. **Rate limit hit** → Switch to another engine

### **Graceful Degradation**
```python
# Example of fallback behavior
results = search_tools.web_search("query")
# If Serper fails, tries Tavily
# If Tavily fails, tries Google
# If all fail, returns mock results
```

## 📈 Performance Monitoring

### **Search Statistics**
```python
stats = search_tools.get_search_stats()
print(stats)
# Output:
# {
#   "available_engines": ["serper", "tavily"],
#   "default_engine": "serper",
#   "serper_configured": true,
#   "tavily_configured": true
# }
```

### **Logging**
- All searches logged with query and results count
- Errors logged with fallback attempts
- Performance metrics tracked

## 🔒 Security Best Practices

### **API Key Management**
```bash
# Use environment variables (never hardcode)
export SERPER_API_KEY="your-key"

# Or use .env file
echo "SERPER_API_KEY=your-key" >> .env
```

### **Rate Limiting**
- Built-in rate limiting per engine
- Automatic engine switching on limits
- Request timeout protection

## 🚀 Production Deployment

### **Docker Environment**
```yaml
# docker-compose.yml
environment:
  - SERPER_API_KEY=${SERPER_API_KEY}
  - TAVILY_API_KEY=${TAVILY_API_KEY}
```

### **Kubernetes Config**
```yaml
# k8s-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: search-keys
data:
  SERPER_API_KEY: <base64-encoded-key>
  TAVILY_API_KEY: <base64-encoded-key>
```

## 📞 Troubleshooting

### **Common Issues**

**1. "No search engines available"**
```bash
# Check environment variables
echo $SERPER_API_KEY
echo $TAVILY_API_KEY

# Verify API keys are valid
curl -H "X-API-KEY: $SERPER_API_KEY" "https://api.serper.dev/search?q=test"
```

**2. "Search failed" errors**
```bash
# Check network connectivity
curl -I https://api.serper.dev
curl -I https://api.tavily.com

# Verify API key permissions
# Check API console for usage limits
```

**3. "Rate limit exceeded"**
- System automatically switches engines
- Consider upgrading API plan
- Implement caching for repeated queries

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Test with detailed logging
search = WebSearchIntegration()
results = search.search("test query")
```

## 🎉 Getting Started

1. **Choose your search engines** (Serper + Tavily recommended)
2. **Get API keys** from respective providers
3. **Configure environment variables**
4. **Test integration** with sample queries
5. **Deploy with Docker** or your preferred method

Your Email Assistant now has powerful, multi-engine web search capabilities! 🚀
