"""
Utility helpers for the content generator
"""
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent

def ensure_asset_directory() -> Path:
    """Ensure assets directory exists"""
    assets_dir = get_project_root() / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    return assets_dir

def load_logo() -> Optional[Path]:
    """
    Load the EAVN logo
    
    Returns:
        Path to logo file if exists, None otherwise
    """
    assets_dir = ensure_asset_directory()
    logo_path = assets_dir / "logo_eavn.png"
    
    if not logo_path.exists():
        # Try alternative names
        for alt_name in ["logo.png", "logo_eavn.jpg", "eavn_logo.png"]:
            alt_path = assets_dir / alt_name
            if alt_path.exists():
                logo_path = alt_path
                break
    
    if not logo_path.exists():
        logger.warning(f"Logo not found at {logo_path}")
        return None
    
    return logo_path

def create_content_with_logo(
    content: str,
    logo_path: Optional[str] = None
) -> str:
    """
    Add logo reference to content
    
    Args:
        content: Original content
        logo_path: Path to logo file
    
    Returns:
        Content with logo reference
    """
    if logo_path:
        logo_note = f"\n\n[Ảnh: {logo_path}]"
        return content + logo_note
    else:
        # Add placeholder for logo
        logo_note = "\n\n[Logo EAVN sẽ được hiển thị]"
        return content + logo_note

def send_to_all_platforms(
    content: str,
    platforms: List[str],
    logo_path: Optional[str] = None,
    publishers: dict = None
):
    """
    Send content to multiple platforms
    
    Args:
        content: Content to publish
        platforms: List of platform names
        logo_path: Optional logo path
        publishers: Dictionary of platform publishers
    """
    from social_platforms import FacebookPublisher, LinkedInPublisher, InstagramPublisher, ZaloPublisher
    
    platform_publishers = {
        "facebook": FacebookPublisher if publishers is None else publishers.get("facebook"),
        "linkedin": LinkedInPublisher if publishers is None else publishers.get("linkedin"),
        "instagram": InstagramPublisher if publishers is None else publishers.get("instagram"),
        "zalo": ZaloPublisher if publishers is None else publishers.get("zalo"),
    }
    
    results = {}
    
    for platform in platforms:
        if platform in platform_publishers and platform_publishers[platform]:
            publisher = platform_publishers[platform]
            result = publisher.publish(content, logo_path)
            results[platform] = result
            logger.info(f"{platform}: {'✓' if result.success else '✗'} {result.message}")
    
    return results

def create_email_html(
    subject: str,
    content: str,
    logo_path: Optional[str] = None,
    contact_email: Optional[str] = None
) -> str:
    """
    Create HTML email content
    
    Args:
        subject: Email subject
        content: Email body text
        logo_path: Optional logo path
        contact_email: Optional contact email
    
    Returns:
        HTML string
    """
    # Escape HTML
    import html
    
    escaped_content = html.escape(content)
    
    # Logo HTML
    logo_html = ""
    if logo_path:
        logo_html = f'<img src="cid:logo_eavn" alt="Logo EAVN" style="max-width: 200px; margin-bottom: 20px;">'
    else:
        logo_html = '<div style="background: #0066cc; color: white; padding: 10px; text-align: center; margin-bottom: 20px; font-weight: bold;">EAVN - Eastern Access Vietnam</div>'
    
    # Contact HTML
    contact_html = ""
    if contact_email:
        contact_html = f'<p>📧 Liên hệ: <a href="mailto:{contact_email}">{contact_email}</a></p>'
    else:
        contact_html = '<p>📧 Liên hệ: [Điền email của bạn vào đây]</p>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        {logo_html}
        <h1 style="color: #0066cc;">{html.escape(subject)}</h1>
        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            {escaped_content}
        </div>
        {contact_html}
        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
        <p style="font-size: 12px; color: #666; text-align: center;">
            EAVN - Eastern Access Vietnam<br>
            🌐 eascs.com.vn
        </p>
    </body>
    </html>
    """
    
    return html_content

def format_timestamp(dt: datetime) -> str:
    """Format datetime to readable string"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_content_today_summary(results: dict) -> str:
    """Get summary of today's content generation"""
    summary = []
    summary.append(f"=== Nội Dung Hôm Nay ({datetime.now().strftime('%Y-%m-%d')}) ===")
    
    for platform, result in results.items():
        status = "✓ Thành công" if result.get("success") else "✗ Thất bại"
        summary.append(f"- {platform}: {status}")
    
    return "\n".join(summary)
