"""
Instagram Publisher - Publishes content to Instagram Business Accounts
"""
import logging
from typing import Optional
from .base import BasePlatformPublisher, PostResult, MockPlatformPublisher

logger = logging.getLogger(__name__)

class InstagramPublisher(BasePlatformPublisher):
    """Publisher for Instagram using Graph API"""
    
    def _get_platform_name(self) -> str:
        return "Instagram"
    
    def publish(self, content: str, media_path: Optional[str] = None) -> PostResult:
        """Publish content to Instagram Business Account"""
        if not self._check_credentials():
            logger.warning("Instagram credentials not configured. Using mock.")
            return self._mock_publish(content, media_path)
        
        # Instagram requires media for posts, cannot post text-only
        if not media_path:
            logger.warning("Instagram requires media for posts. Please provide an image.")
            return PostResult(
                success=False,
                platform="Instagram",
                message="Instagram post requires media",
                error="No media file provided",
                timestamp=__import__('datetime').datetime.now().isoformat()
            )
        
        try:
            import requests
            
            account_id = self._get_config("business_account_id")
            access_token = self._get_config("access_token")
            api_version = self._get_config("api_version", "v18.0")
            
            if not account_id or not access_token:
                logger.warning("Instagram account_id or access_token not set. Using mock.")
                return self._mock_publish(content, media_path)
            
            # Step 1: Create a media container
            container_url = f"https://graph.facebook.com/{api_version}/{account_id}/media"
            
            with open(media_path, "rb") as f:
                # For Instagram, we need to upload the image first
                files = {"image": ("image.jpg", f, "image/jpeg")}
                data = {
                    "caption": content,
                    "access_token": access_token
                }
                
                response = requests.post(container_url, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    creation_id = result.get("id", "")
                    
                    # Step 2: Publish the container
                    publish_url = f"https://graph.facebook.com/{api_version}/{account_id}/media_publish"
                    publish_data = {
                        "creation_id": creation_id,
                        "access_token": access_token
                    }
                    
                    publish_response = requests.post(publish_url, json=publish_data)
                    
                    if publish_response.status_code == 200:
                        publish_result = publish_response.json()
                        post_id = publish_result.get("id", "")
                        
                        return PostResult(
                            success=True,
                            platform="Instagram",
                            post_id=post_id,
                            message="Published successfully",
                            timestamp=__import__('datetime').datetime.now().isoformat()
                        )
                    else:
                        error_msg = publish_response.text
                        logger.error(f"Instagram publish error: {error_msg}")
                        return PostResult(
                            success=False,
                            platform="Instagram",
                            message="Failed to publish",
                            error=error_msg,
                            timestamp=__import__('datetime').datetime.now().isoformat()
                        )
                else:
                    error_msg = response.text
                    logger.error(f"Instagram container error: {error_msg}")
                    return PostResult(
                        success=False,
                        platform="Instagram",
                        message="Failed to create container",
                        error=error_msg,
                        timestamp=__import__('datetime').datetime.now().isoformat()
                    )
                        
        except Exception as e:
            logger.error(f"Error publishing to Instagram: {e}")
            return PostResult(
                success=False,
                platform="Instagram",
                message="Error publishing",
                error=str(e),
                timestamp=__import__('datetime').datetime.now().isoformat()
            )
    
    def _mock_publish(self, content: str, media_path: Optional[str] = None) -> PostResult:
        """Mock publish for testing"""
        logger.info(f"[MOCK INSTAGRAM] Would publish: {content[:50]}...")
        logger.info(f"[MOCK INSTAGRAM] Media: {media_path}")
        
        return PostResult(
            success=True,
            platform="Instagram",
            post_id="mock_ig_001",
            message="Mock post created - configure credentials to publish for real (requires media)",
            timestamp=__import__('datetime').datetime.now().isoformat()
        )
