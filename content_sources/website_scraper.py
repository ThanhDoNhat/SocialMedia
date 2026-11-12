"""
Website scraper module - Extracts content from product websites
"""
import logging
import re
from typing import Optional
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

@dataclass
class ScrapedContent:
    """Represents scraped content from a webpage"""
    url: str
    title: str
    description: str
    body_text: str
    keywords: list[str]
    scraped_at: str

class WebsiteScraper:
    """Scrapes content from websites"""
    
    # Headers to avoid being blocked
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
        })
    
    def scrape(self, url: str) -> Optional[ScrapedContent]:
        """Scrape content from a URL"""
        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # Remove script, style, nav, footer elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Get title
            title = self._extract_title(soup)
            
            # Get meta description
            description = self._extract_meta_description(soup)
            
            # Get main body text
            body_text = self._extract_body_text(soup)
            
            # Extract keywords from meta tags
            keywords = self._extract_keywords(soup)
            
            return ScrapedContent(
                url=url,
                title=title,
                description=description,
                body_text=body_text,
                keywords=keywords,
                scraped_at=__import__('datetime').datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)
        
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        
        return "No title found"
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"]
        
        # Try og:description
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        if og_desc and og_desc.get("content"):
            return og_desc["content"]
        
        return ""
    
    def _extract_body_text(self, soup: BeautifulSoup) -> str:
        """Extract main body text"""
        # Try to find main content area
        main = soup.find("main")
        if main:
            return main.get_text(strip=True)
        
        article = soup.find("article")
        if article:
            return article.get_text(strip=True)
        
        # Fallback to body
        body = soup.find("body")
        if body:
            return body.get_text(strip=True)
        
        return soup.get_text(strip=True)
    
    def _extract_keywords(self, soup: BeautifulSoup) -> list[str]:
        """Extract keywords from meta tags"""
        keywords = []
        
        # From meta keywords
        meta_kw = soup.find("meta", attrs={"name": "keywords"})
        if meta_kw and meta_kw.get("content"):
            keywords.extend(
                [kw.strip() for kw in meta_kw["content"].split(",")]
            )
        
        # From h1, h2, h3 tags
        for tag in soup.find_all(["h1", "h2", "h3"]):
            text = tag.get_text(strip=True)
            if text and len(text) > 3:
                keywords.append(text)
        
        return keywords[:10]  # Limit to 10 keywords


class ProductWebsiteScraper:
    """Specialized scraper for product-related websites"""
    
    def __init__(self):
        self.scraper = WebsiteScraper()
        # Specific selectors for each product site
        self.selectors = {
            "toshiba": {
                "title": "h1.product-title, .product-name",
                "description": ".product-description, [data-description]",
                "features": ".features-list li, .product-features li",
            },
            "synology": {
                "title": "h1.title, .ProductDetails-title",
                "description": ".description, .product-intro",
            },
            "wasabi": {
                "title": "h1, .hero-title",
                "description": ".hero-subtitle, .subtitle",
            },
        }
    
    def scrape_product(self, url: str) -> Optional[ScrapedContent]:
        """Scrape a product page with optimized extraction"""
        content = self.scraper.scrape(url)
        if content:
            # Add product-specific details
            product_info = self._extract_product_details(url, content)
            content.description = product_info or content.description
        return content
    
    def _extract_product_details(self, url: str, content: ScrapedContent) -> Optional[str]:
        """Extract product-specific details based on URL"""
        domain = urlparse(url).netloc.lower()
        
        details = []
        
        if "toshiba" in domain:
            details.append("[Toshiba Storage]")
        elif "synology" in domain:
            details.append("[Synology NAS]")
        elif "wasabi" in domain:
            details.append("[Wasabi Cloud Storage]")
        elif "eascs" in domain or "eastern" in domain:
            details.append("[EAVN - Eastern Access Vietnam]")
        elif "aucore" in domain:
            details.append("[AurCore Technology]")
        
        return " ".join(details) + " " + content.description if details else None
