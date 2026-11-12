"""
Facebook Publisher - Publishes content to Facebook Pages
"""
import logging
from typing import Optional
from .base import BasePlatformPublisher, PostResult, MockPlatformPublisher

logger = logging.getLogger(__name__)

class FacebookPublisher(BasePlatformPublisher):
    """Publisher for Facebook Pages using Graph API"""
    
    def _get_platform_name(self) -> str:
        return "Facebook"
    
    def publish(self, content: str, media_path: Optional[str] = None) -> PostResult:
        """Publish content to Facebook Page"""
        if not self._check_credentials():
            logger.warning("Facebook credentials not configured. Using mock.")
            return self._mock_publish(content, media_path)
        
        try:
            # Get credentials
            page_id = self._get_config("page_id")
            access_token = self._get_config("access_token")
            api_version = self._get_config("api_version", "v18.0")
            
            if not page_id or not access_token:
                logger.warning("Facebook page_id or access_token not set. Using mock.")
                return self._mock_publish(content, media_path)
            
            # Facebook Graph API endpoint
            import requests
            
            api_url = f"https://graph.facebook.com/{api_version}/{page_id}/feed"
            
            # Prepare payload
            payload = {
                "message": content,
                "access_token": access_token
            }
            
            # If there's media, upload it first
            if media_path:
                # Upload photo first
                media_upload_url = f"https://graph.facebook.com/{api_version}/{page_id}/photos"
                with open(media_path, "rb") as f:
                    files = {"source": f}
                    data = {"access_token": access_token, "message": content}
                    response = requests.post(media_upload_url, files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        post_id = result.get("id", "")
                        
                        return PostResult(
                            success=True,
                            platform="Facebook",
                            post_id=post_id,
                            message="Published with photo",
                            timestamp=__import__('datetime').datetime.now().isoformat()
                        )
            
            # Publish text post
            response = requests.post(api_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get("id", "")
                
                return PostResult(
                    success=True,
                    platform="Facebook",
                    post_id=post_id,
                    message="Published successfully",
                    timestamp=__import__('datetime').datetime.now().isoformat()
                )
            else:
                error_msg = response.text
                logger.error(f"Facebook API error: {error_msg}")
                return PostResult(
                    success=False,
                    platform="Facebook",
                    message="Failed to publish",
                    error=error_msg,
                    timestamp=__import__('datetime').datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"Error publishing to Facebook: {e}")
            return PostResult(
                success=False,
                platform="Facebook",
                message="Error publishing",
                error=str(e),
                timestamp=__import__('datetime').datetime.now().isoformat()
            )
    
    def _mock_publish(self, content: str, media_path: Optional[str] = None) -> PostResult:
        """Mock publish for testing"""
        logger.info(f"[MOCK FACEBOOK] Would publish: {content[:50]}...")
        logger.info(f"[MOCK FACEBOOK] Media: {media_path}")
        
        return PostResult(
            success=True,
            platform="Facebook",
            post_id="mock_fb_001",
            message="Mock post created - configure credentials to publish for real",
            timestamp=__import__('datetime').datetime.now().isoformat()
        )


# Default to mock for testing
FacebookPublisher = FacebookPublisher
