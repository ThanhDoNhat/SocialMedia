"""
Source Manager - Coordinates all content sources
"""
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from .website_scraper import ProductWebsiteScraper, ScrapedContent
from .online_news import OnlineContentResearch, NewsArticle

@dataclass
class ContentItem:
    """Unified content item from any source"""
    source_type: str  # "website", "news", "internal"
    title: str
    content: str
    source_url: Optional[str]
    source_name: str
    relevance_score: float
    scraped_at: str

class SourceManager:
    """Manages all content sources and collects content"""
    
    def __init__(self, websites: list[str] = None, enable_online: bool = True):
        self.product_scraper = ProductWebsiteScraper()
        self.online_research = OnlineContentResearch() if enable_online else None
        self.websites = websites or []
        
        # Queue for content to process
        self.content_queue = []
    
    def collect_from_websites(self) -> list[ContentItem]:
        """Collect content from product websites"""
        items = []
        
        for url in self.websites:
            try:
                content = self.product_scraper.scrape_product(url)
                if content:
                    item = ContentItem(
                        source_type="website",
                        title=content.title,
                        content=content.description + " " + content.body_text[:500],
                        source_url=content.url,
                        source_name=self._get_source_name(url),
                        relevance_score=0.8,
                        scraped_at=content.scraped_at
                    )
                    items.append(item)
                    logger.info(f"Collected from {url}: {content.title[:50]}...")
            except Exception as e:
                logger.error(f"Error collecting from {url}: {e}")
        
        return items
    
    def collect_from_online(self) -> list[ContentItem]:
        """Collect relevant online news and content"""
        items = []
        
        if self.online_research:
            try:
                results = self.online_research.search()
                
                for result in results[:5]:
                    item = ContentItem(
                        source_type="news",
                        title=result.get("title", "Untitled"),
                        content=result.get("snippet", ""),
                        source_url=result.get("url"),
                        source_name=result.get("source", "Online"),
                        relevance_score=0.6,
                        scraped_at=__import__('datetime').datetime.now().isoformat()
                    )
                    items.append(item)
                    
            except Exception as e:
                logger.error(f"Error collecting from online: {e}")
        
        return items
    
    def collect_all(self) -> list[ContentItem]:
        """Collect content from all sources"""
        all_items = []
        
        # Collect from websites
        website_items = self.collect_from_websites()
        all_items.extend(website_items)
        
        # Collect from online
        online_items = self.collect_from_online()
        all_items.extend(online_items)
        
        logger.info(f"Collected {len(all_items)} content items from all sources")
        
        return all_items
    
    def _get_source_name(self, url: str) -> str:
        """Get friendly source name from URL"""
        domains = {
            "eascs.com.vn": "EAVN",
            "toshiba-storage.com": "Toshiba Storage",
            "aucore-tech.com": "AurCore Technology",
            "wasabi.com": "Wasabi Cloud Storage",
            "synology.com": "Synology",
        }
        
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        
        for key, name in domains.items():
            if key in domain:
                return name
        
        return domain
