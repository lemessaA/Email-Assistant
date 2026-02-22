"""
Web Search Integration Module

This module provides multiple web search services for the Email Assistant.
It supports Serper API for general searches and Tavily AI for AI-optimized searches.
"""

import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class SearchEngine(Enum):
    """Available search engines"""
    SERPER = "serper"
    TAVILY = "tavily"
    GOOGLE = "google"
    BING = "bing"

class WebSearchIntegration:
    """
    Multi-engine web search integration for email assistant
    """
    
    def __init__(self):
        """Initialize web search services"""
        self.serper_api_key = os.getenv("SERPER_API_KEY", "")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY", "")
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY", "")
        self.google_cx = os.getenv("GOOGLE_SEARCH_CX", "")
        self.bing_api_key = os.getenv("BING_SEARCH_API_KEY", "")
        
        # Default search engine
        self.default_engine = SearchEngine.SERPER
        
        # Check available engines
        self.available_engines = self._check_available_engines()
        logger.info(f"Available search engines: {[e.value for e in self.available_engines]}")
    
    def _check_available_engines(self) -> List[SearchEngine]:
        """Check which search engines are properly configured"""
        engines = []
        
        if self.serper_api_key and self.serper_api_key != "your-api-key":
            engines.append(SearchEngine.SERPER)
        
        if self.tavily_api_key and self.tavily_api_key != "your-api-key":
            engines.append(SearchEngine.TAVILY)
        
        if self.google_api_key and self.google_cx:
            engines.append(SearchEngine.GOOGLE)
        
        if self.bing_api_key and self.bing_api_key != "your-api-key":
            engines.append(SearchEngine.BING)
        
        return engines
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        engine: Optional[SearchEngine] = None,
        search_type: str = "general"
    ) -> List[Dict[str, Any]]:
        """
        Perform web search with specified or best available engine
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            engine: Specific search engine to use (auto-selects if None)
            search_type: Type of search (general, ai_context, news, etc.)
            
        Returns:
            List of search results
        """
        # Select engine
        if engine is None:
            engine = self._select_best_engine(search_type)
        
        # Check if engine is available
        if engine not in self.available_engines:
            logger.warning(f"Search engine {engine.value} not available, falling back to {self.default_engine.value}")
            engine = self.default_engine
        
        if engine not in self.available_engines:
            logger.error("No search engines available")
            return []
        
        # Perform search based on engine
        try:
            if engine == SearchEngine.SERPER:
                return self._serper_search(query, max_results)
            elif engine == SearchEngine.TAVILY:
                return self._tavily_search(query, max_results, search_type)
            elif engine == SearchEngine.GOOGLE:
                return self._google_search(query, max_results)
            elif engine == SearchEngine.BING:
                return self._bing_search(query, max_results)
            else:
                logger.error(f"Unknown search engine: {engine}")
                return []
                
        except Exception as e:
            logger.error(f"Search failed with {engine.value}: {str(e)}")
            # Try fallback engine
            return self._fallback_search(query, max_results, engine)
    
    def _select_best_engine(self, search_type: str) -> SearchEngine:
        """Select best engine based on search type"""
        if search_type == "ai_context" and SearchEngine.TAVILY in self.available_engines:
            return SearchEngine.TAVILY
        elif search_type == "news" and SearchEngine.BING in self.available_engines:
            return SearchEngine.BING
        elif SearchEngine.SERPER in self.available_engines:
            return SearchEngine.SERPER
        elif self.available_engines:
            return self.available_engines[0]
        else:
            return self.default_engine
    
    def _serper_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Serper API (Google results)"""
        try:
            response = requests.get(
                "https://api.serper.dev/search",
                params={
                    "q": query,
                    "num": max_results
                },
                headers={
                    "X-API-KEY": self.serper_api_key,
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Process organic results
                for item in data.get("organic", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "serper",
                        "position": item.get("position", 0)
                    })
                
                # Add knowledge graph if available
                if data.get("knowledgeGraph"):
                    results.append({
                        "title": data["knowledgeGraph"].get("title", ""),
                        "link": data["knowledgeGraph"].get("descriptionLink", ""),
                        "snippet": data["knowledgeGraph"].get("description", ""),
                        "source": "serper_knowledge",
                        "type": "knowledge_graph"
                    })
                
                logger.info(f"Serper search returned {len(results)} results")
                return results
            else:
                logger.error(f"Serper API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Serper search failed: {str(e)}")
            return []
    
    def _tavily_search(self, query: str, max_results: int, search_type: str = "general") -> List[Dict[str, Any]]:
        """Search using Tavily AI API (AI-optimized)"""
        try:
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": search_type == "ai_context",
                "include_raw_content": False,
                "max_results": max_results,
                "include_domains": [],
                "exclude_domains": []
            }
            
            # Add search type specific parameters
            if search_type == "news":
                payload["search_depth"] = "advanced"
                payload["include_domains"] = ["news.google.com", "cnn.com", "bbc.com", "reuters.com"]
            elif search_type == "academic":
                payload["include_domains"] = ["scholar.google.com", "arxiv.org", "pubmed.ncbi.nlm.nih.gov"]
            
            response = requests.post(
                "https://api.tavily.com/search",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Process search results
                for item in data.get("results", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("url", ""),
                        "snippet": item.get("content", ""),
                        "source": "tavily",
                        "score": item.get("score", 0),
                        "published_date": item.get("publishedDate", "")
                    })
                
                # Add AI answer if available
                if data.get("answer"):
                    results.insert(0, {
                        "title": "AI Answer",
                        "link": "",
                        "snippet": data["answer"],
                        "source": "tavily_ai",
                        "type": "ai_answer"
                    })
                
                logger.info(f"Tavily search returned {len(results)} results")
                return results
            else:
                logger.error(f"Tavily API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Tavily search failed: {str(e)}")
            return []
    
    def _google_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API"""
        try:
            response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": self.google_api_key,
                    "cx": self.google_cx,
                    "q": query,
                    "num": max_results
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("items", [])[:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "google",
                        "display_link": item.get("displayLink", "")
                    })
                
                logger.info(f"Google search returned {len(results)} results")
                return results
            else:
                logger.error(f"Google API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Google search failed: {str(e)}")
            return []
    
    def _bing_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Bing Search API"""
        try:
            response = requests.get(
                "https://api.bing.microsoft.com/v7.0/search",
                params={
                    "q": query,
                    "count": max_results,
                    "mkt": "en-US"
                },
                headers={
                    "Ocp-Apim-Subscription-Key": self.bing_api_key
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("webPages", {}).get("value", [])[:max_results]:
                    results.append({
                        "title": item.get("name", ""),
                        "link": item.get("url", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "bing",
                        "date_last_crawled": item.get("dateLastCrawled", "")
                    })
                
                logger.info(f"Bing search returned {len(results)} results")
                return results
            else:
                logger.error(f"Bing API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Bing search failed: {str(e)}")
            return []
    
    def _fallback_search(self, query: str, max_results: int, failed_engine: SearchEngine) -> List[Dict[str, Any]]:
        """Try fallback search engines"""
        fallback_engines = [e for e in self.available_engines if e != failed_engine]
        
        for engine in fallback_engines:
            try:
                logger.info(f"Trying fallback engine: {engine.value}")
                if engine == SearchEngine.SERPER:
                    return self._serper_search(query, max_results)
                elif engine == SearchEngine.TAVILY:
                    return self._tavily_search(query, max_results)
                elif engine == SearchEngine.GOOGLE:
                    return self._google_search(query, max_results)
                elif engine == SearchEngine.BING:
                    return self._bing_search(query, max_results)
            except Exception as e:
                logger.warning(f"Fallback engine {engine.value} also failed: {str(e)}")
                continue
        
        logger.error("All search engines failed")
        return []
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get statistics about available search engines"""
        return {
            "available_engines": [e.value for e in self.available_engines],
            "default_engine": self.default_engine.value,
            "serper_configured": bool(self.serper_api_key and self.serper_api_key != "your-api-key"),
            "tavily_configured": bool(self.tavily_api_key and self.tavily_api_key != "your-api-key"),
            "google_configured": bool(self.google_api_key and self.google_cx),
            "bing_configured": bool(self.bing_api_key and self.bing_api_key != "your-api-key")
        }
