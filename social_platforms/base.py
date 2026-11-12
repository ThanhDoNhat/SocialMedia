"""
Base Platform Publisher - Base class for all social media platforms
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PostResult:
    """Result of a post operation"""
    success: bool
    platform: str
    post_id: Optional[str] = None
    message: str = ""
    error: Optional[str] = None
    timestamp: str = ""

class BasePlatformPublisher(ABC):
    """Abstract base class for platform publishers"""
    
    def __init__(self, config: dict):
        self.config = config
        self.platform_name = self._get_platform_name()
        self.enabled = config.get("enabled", False)
        
        if not self.enabled:
            logger.info(f"{self.platform_name} is disabled")
    
    @abstractmethod
    def _get_platform_name(self) -> str:
        """Get platform name"""
        pass
    
    @abstractmethod
    def publish(self, content: str, media_path: Optional[str] = None) -> PostResult:
        """Publish content to the platform"""
        pass
    
    def _get_config(self, key: str, default: str = "") -> str:
        """Get configuration value safely"""
        return self.config.get(key, default)
    
    def _check_credentials(self) -> bool:
        """Check if credentials are configured"""
        return self.enabled


class MockPlatformPublisher(BasePlatformPublisher):
    """Mock publisher for testing without actual API access"""
    
    def _get_platform_name(self) -> str:
        return "Mock"
    
    def publish(self, content: str, media_path: Optional[str] = None) -> PostResult:
        """Mock publish - just logs the content"""
        logger.info(f"[MOCK] Publishing to {self.platform_name}:")
        logger.info(f"[MOCK] Content: {content[:100]}...")
        
        if media_path:
            logger.info(f"[MOCK] Media: {media_path}")
        
        return PostResult(
            success=True,
            platform=self.platform_name,
            post_id="mock_post_123",
            message="Mock post created",
            timestamp=__import__('datetime').datetime.now().isoformat()
        )


import datetime
