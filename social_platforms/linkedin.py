"""
LinkedIn Publisher - Publishes content to LinkedIn Company Pages
"""
import logging
from typing import Optional
from .base import BasePlatformPublisher, PostResult, MockPlatformPublisher

logger = logging.getLogger(__name__)

class LinkedInPublisher(BasePlatformPublisher):
    """Publisher for LinkedIn using API"""
    
    def _get_platform_name(self) -> str:
        return "LinkedIn"
    
    def publish(self, content: str, media_path: Optional[str] = None) -> PostResult:
        """Publish content to LinkedIn Company Page"""
        if not self._check_credentials():
            logger.warning("LinkedIn credentials not configured. Using mock.")
            return self._mock_publish(content, media_path)
        
        try:
            import requests
            
            company_id = self._get_config("company_id")
            access_token = self._get_config("access_token")
            api_version = self._get_config("api_version", "v2")
            
            if not company_id or not access_token:
                logger.warning("LinkedIn company_id or access_token not set. Using mock.")
                return self._mock_publish(content, media_path)
            
            # LinkedIn API endpoint for company posts
            api_url = f"https://api.linkedin.com/{api_version}/companies/{company_id}/shares"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # Prepare post body
            post_body = {
                "commentary": content,
                "visibility": {
                    "code": "anyone"
                }
            }
            
            payload = {
                "author": f"urn:li:company:{company_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = requests.post(api_url, json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                result = response.json()
                post_id = result.get("id", "")
                
                return PostResult(
                    success=True,
                    platform="LinkedIn",
                    post_id=post_id,
                    message="Published successfully",
                    timestamp=__import__('datetime').datetime.now().isoformat()
                )
            else:
                error_msg = response.text
                logger.error(f"LinkedIn API error: {error_msg}")
                return PostResult(
                    success=False,
                    platform="LinkedIn",
                    message="Failed to publish",
                    error=error_msg,
                    timestamp=__import__('datetime').datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"Error publishing to LinkedIn: {e}")
            return PostResult(
                success=False,
                platform="LinkedIn",
                message="Error publishing",
                error=str(e),
                timestamp=__import__('datetime').datetime.now().isoformat()
            )
    
    def _mock_publish(self, content: str, media_path: Optional[str] = None) -> PostResult:
        """Mock publish for testing"""
        logger.info(f"[MOCK LINKEDIN] Would publish: {content[:50]}...")
        logger.info(f"[MOCK LINKEDIN] Media: {media_path}")
        
        return PostResult(
            success=True,
            platform="LinkedIn",
            post_id="mock_li_001",
            message="Mock post created - configure credentials to publish for real",
            timestamp=__import__('datetime').datetime.now().isoformat()
        )
