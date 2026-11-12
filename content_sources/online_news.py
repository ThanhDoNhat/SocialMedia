"""
Online news module - Finds technology and solution news online
"""
import logging
import feedparser
from typing import Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """Represents a news article"""
    title: str
    source: str
    url: str
    summary: str
    published_date: Optional[str]
    content: str

class OnlineNewsFinder:
    """Finds relevant technology news online"""
    
    # Technology and solution-related RSS feeds
    DEFAULT_FEEDS = [
        # Vietnamese tech news
        "https://vietnamnet.vn/rsscn.rss",
        "https://tuoitre.vn/rss/cong-nghe.rss",
        
        # International tech
        "https://www.techmeme.com/feed",
        "https://feeds.feedburner.com/Techmeme",
        
        # Storage and cloud related
        "https://www.storagereview.com/feed/",
    ]
    
    # Keywords for filtering relevant content
    RELEVANT_KEYWORDS = [
        "lưu trữ", "storage", "hard drive", "HDD", "SSD", "NAS",
        "cloud", "cloud storage", "dữ liệu", "data", "backup",
        "synology", "toshiba", "wasabi", "server", "IT solution",
        "giải pháp", "doanh nghiệp", "enterprise", "business solution",
    ]
    
    def __init__(self, custom_feeds: list[str] = None):
        self.feeds = custom_feeds or self.DEFAULT_FEEDS
    
    def find_relevant_news(self, limit: int = 5) -> list[NewsArticle]:
        """Find relevant technology news from RSS feeds"""
        articles = []
        
        for feed_url in self.feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:limit]:
                    article = self._parse_entry(entry, feed.feed.get("title", "Unknown"))
                    if article and self._is_relevant(article):
                        articles.append(article)
                        
                        if len(articles) >= limit:
                            return articles
                            
            except Exception as e:
                logger.warning(f"Error parsing feed {feed_url}: {e}")
                continue
        
        return articles
    
    def _parse_entry(self, entry, source: str) -> Optional[NewsArticle]:
        """Parse a feed entry into NewsArticle"""
        try:
            title = entry.get("title", "No Title")
            url = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))
            published = entry.get("published", entry.get("updated"))
            
            return NewsArticle(
                title=title,
                source=source,
                url=url,
                summary=summary,
                published_date=published,
                content=summary
            )
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None
    
    def _is_relevant(self, article: NewsArticle) -> bool:
        """Check if article is relevant to our business"""
        text = (article.title + " " + article.summary).lower()
        
        for keyword in self.RELEVANT_KEYWORDS:
            if keyword.lower() in text:
                return True
        
        return False
    
    def fetch_article_content(self, url: str) -> Optional[NewsArticle]:
        """Fetch full article content from URL"""
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # Remove script and style
            for tag in soup(["script", "style"]):
                tag.decompose()
            
            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else "No Title"
            
            # Try to get main article content
            article = soup.find("article") or soup.find("main")
            content = article.get_text(strip=True) if article else soup.get_text(strip=True)
            
            return NewsArticle(
                title=title_text,
                source=url,
                url=url,
                summary=content[:500],  # First 500 chars as summary
                published_date=None,
                content=content[:2000]   # First 2000 chars
            )
        except Exception as e:
            logger.error(f"Error fetching article {url}: {e}")
            return None


class OnlineContentResearch:
    """Research online for relevant content"""
    
    def __init__(self):
        self.news_finder = OnlineNewsFinder()
    
    def search(self, query: str = None) -> list[dict]:
        """Search for relevant content online"""
        results = []
        
        # Get tech news
        articles = self.news_finder.find_relevant_news(limit=10)
        
        for article in articles:
            results.append({
                "type": "news",
                "title": article.title,
                "source": article.source,
                "url": article.url,
                "snippet": article.summary,
                "relevance": "technology"
            })
        
        return results
    
    def research_by_topic(self, topic: str, max_results: int = 5) -> list[dict]:
        """Research content by specific topic"""
        # For now, filter existing news results
        all_results = self.search()
        filtered = []
        
        for result in all_results:
            combined_text = (result.get("title", "") + " " + 
                           result.get("snippet", "")).lower()
            
            if topic.lower() in combined_text:
                filtered.append(result)
            
            if len(filtered) >= max_results:
                break
        
        return filtered
