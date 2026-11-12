"""
Zalo Publisher - Publishes content to Zalo OA (Official Account)
"""
import logging
from typing import Optional
from .base import BasePlatformPublisher, PostResult, MockPlatformPublisher

logger = logging.getLogger(__name__)

class ZaloPublisher(BasePlatformPublisher):
    """Publisher for Zalo OA using Zalo Open API"""
    
    def _get_platform_name(self) -> str:
        return "Zalo"
    
    def publish(self, content: str, media_path: Optional[str] = None) -> PostResult:
        """Publish content to Zalo OA"""
        if not self._check_credentials():
            logger.warning("Zalo credentials not configured. Using mock.")
            return self._mock_publish(content, media_path)
        
        try:
            import requests
            
            oa_id = self._get_config("oa_id")
            access_token = self._get_config("access_token")
            api_url = self._get_config("api_url", "https://open.zalo.me")
            
            if not oa_id or not access_token:
                logger.warning("Zalo OA ID or access_token not set. Using mock.")
                return self._mock_publish(content, media_path)
            
            # Zalo OA API - send message
            # https://open.zalo.me/docs/#/zalo-open-api/gửi-nội-dung
            
            if media_path:
                # Upload media and send
                media_url = f"{api_url}/v2.0/{oa_id}/oaicongtai/upload"
                with open(media_path, "rb") as f:
                    files = {"file": f}
                    data = {"access_token": access_token}
                    response = requests.post(media_url, files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        media_id = result.get("media_id", "")
                        
                        # Send message with media
                        send_url = f"{api_url}/v2.0/{oa_id}/oaicontents"
                        payload = {
                            "content": {
                                "type": "media",
                                "media": {
                                    "media_id": media_id
                                }
                            },
                            "access_token": access_token
                        }
                        
                        send_response = requests.post(send_url, json=payload)
                        
                        if send_response.status_code == 200:
                            return PostResult(
                                success=True,
                                platform="Zalo",
                                post_id="sent",
                                message="Published with media",
                                timestamp=__import__('datetime').datetime.now().isoformat()
                            )
            else:
                # Send text message
                send_url = f"{api_url}/v2.0/{oa_id}/oaicontents"
                payload = {
                    "content": {
                        "type": "text",
                        "text": {
                            "content": content
                        }
                    },
                    "access_token": access_token
                }
                
                response = requests.post(send_url, json=payload)
                
                if response.status_code == 200:
                    return PostResult(
                        success=True,
                        platform="Zalo",
                        post_id="sent",
                        message="Text message sent",
                        timestamp=__import__('datetime').datetime.now().isoformat()
                    )
                
                error_msg = response.text
                logger.error(f"Zalo API error: {error_msg}")
                return PostResult(
                    success=False,
                    platform="Zalo",
                    message="Failed to send",
                    error=error_msg,
                    timestamp=__import__('datetime').datetime.now().isoformat()
                )
                
        except Exception as e:
            logger.error(f"Error publishing to Zalo: {e}")
            return PostResult(
                success=False,
                platform="Zalo",
                message="Error publishing",
                error=str(e),
                timestamp=__import__('datetime').datetime.now().isoformat()
            )
    
    def _mock_publish(self, content: str, media_path: Optional[str] = None) -> PostResult:
        """Mock publish for testing"""
        logger.info(f"[MOCK ZALO] Would publish: {content[:50]}...")
        logger.info(f"[MOCK ZALO] Media: {media_path}")
        
        return PostResult(
            success=True,
            platform="Zalo",
            post_id="mock_zalo_001",
            message="Mock post created - configure credentials to publish for real",
            timestamp=__import__('datetime').datetime.now().isoformat()
        )


# For users without Zalo OA credentials, provide a simple alternative using pyzalo if available
class ZaloSimplePublisher(ZaloPublisher):
    """Alternative Zalo publisher using pyzalo library"""
    
    def publish(self, content: str, media_path: Optional[str] = None) -> PostResult:
        """Publish using pyzalo if available"""
        try:
            import pyzalo
            
            # Get Zalo credentials from config
            phone = self._get_config("phone_number")
            password = self._get_config("password")
            
            if not phone or not password:
                logger.warning("Zalo phone or password not set. Using mock.")
                return self._mock_publish(content, media_path)
            
            # Initialize Zalo
            zalo = pyzalo.Zalo(phone, password)
            zalo.login()
            
            # Send message to groups or OA
            # Note: This is a simplified example
            if media_path:
                zalo.send_message_with_file(content, media_path)
            else:
                zalo.send_message(content)
            
            return PostResult(
                success=True,
                platform="Zalo",
                message="Published via pyzalo",
                timestamp=__import__('datetime').datetime.now().isoformat()
            )
            
        except ImportError:
            logger.info("pyzalo not installed. Using base publisher.")
            return super().publish(content, media_path)
        except Exception as e:
            logger.error(f"Error with pyzalo: {e}")
            return self._mock_publish(content, media_path)
