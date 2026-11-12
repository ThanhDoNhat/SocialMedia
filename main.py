#!/usr/bin/env python3
"""
EAVN SocialMedia Content Generator
Main entry point for the application
"""
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
from utils.logger import setup_logging

# Load configuration
from config.settings import (
    AI_MODEL_PROVIDER,
    GEMINI_API_KEY,
    CONTENT_INTERVAL_HOURS,
    PREFERRED_HOUR,
    PRODUCT_WEBSITES,
    SOCIAL_PLATFORMS,
    SMTP_CONFIG,
    EMAIL_SETTINGS,
    CONTENT_STYLE,
    LOG_FILE,
    LOG_LEVEL
)

from content_sources import SourceManager, ContentItem
from content_generator import AIGenerator, GeneratedContent
from social_platforms import FacebookPublisher, LinkedInPublisher, InstagramPublisher, ZaloPublisher
from email_sender import EmailSender, EmailResult
from scheduler import TaskScheduler
from utils.helpers import (
    load_logo,
    create_content_with_logo,
    send_to_all_platforms
)

# Configure logging
setup_logging(LOG_FILE, LOG_LEVEL)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from settings"""
    return {
        "AI_MODEL_PROVIDER": AI_MODEL_PROVIDER,
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "CONTENT_INTERVAL_HOURS": CONTENT_INTERVAL_HOURS,
        "PREFERRED_HOUR": PREFERRED_HOUR,
        "PRODUCT_WEBSITES": PRODUCT_WEBSITES,
        "SOCIAL_PLATFORMS": SOCIAL_PLATFORMS,
        "SMTP_CONFIG": SMTP_CONFIG,
        "EMAIL_SETTINGS": EMAIL_SETTINGS,
        "CONTENT_STYLE": CONTENT_STYLE,
    }


def generate_and_publish(
    contact_email: Optional[str] = None,
    platforms: Optional[list] = None,
    test_mode: bool = False
):
    """
    Main function to generate content and publish
    
    Args:
        contact_email: Contact email for CTA
        platforms: List of platforms to publish to (default: all enabled)
        test_mode: If True, only generate content without publishing
    """
    logger.info("=" * 60)
    logger.info("Starting content generation and publishing process")
    logger.info("=" * 60)
    
    # Load configuration
    config = load_config()
    
    # Step 1: Collect content from sources
    logger.info("\n[1/5] Collecting content from sources...")
    source_manager = SourceManager(
        websites=config["PRODUCT_WEBSITES"],
        enable_online=True
    )
    content_items = source_manager.collect_all()
    
    if not content_items:
        logger.warning("No content collected from sources. Using default topic.")
        content_items = [ContentItem(
            source_type="default",
            title="Giải Pháp Lưu Trữ Dữ Liệu Hiện Đại",
            content="Các giải pháp lưu trữ dữ liệu tiên tiến cho doanh nghiệp: HDD, SSD, NAS, Cloud Storage từ Toshiba, Synology, Wasabi.",
            source_url="",
            source_name="Default",
            relevance_score=0.5,
            scraped_at=""
        )]
    
    # Use the first content item as primary
    primary_content = content_items[0]
    logger.info(f"Primary content: {primary_content.title[:50]}...")
    
    # Step 2: Generate content with AI
    logger.info("\n[2/5] Generating AI content...")
    ai_generator = AIGenerator(config)
    
    # Generate for each platform
    generated_contents = {}
    for platform in platforms or ["facebook", "linkedin", "instagram", "email"]:
        content = ai_generator.generate_content(
            topic=primary_content.title,
            source_content=primary_content.content,
            platform=platform,
            include_logo=True,
            contact_email=contact_email
        )
        generated_contents[platform] = content
        logger.info(f"Generated content for {platform}")
    
    if test_mode:
        logger.info("\n[TEST MODE] Content generated successfully!")
        for platform, content in generated_contents.items():
            logger.info(f"\n--- {platform.upper()} CONTENT ---")
            logger.info(f"Subject: {content.subject}")
            logger.info(f"Content:\n{content.content[:500]}...")
        return
    
    # Step 3: Load logo
    logger.info("\n[3/5] Loading logo...")
    logo_path = load_logo()
    if logo_path:
        logger.info(f"Logo loaded: {logo_path}")
    else:
        logger.warning("Logo not found. Content will be published without logo.")
    
    # Step 4: Publish to social platforms
    logger.info("\n[4/5] Publishing to social platforms...")
    publishers = {
        "facebook": FacebookPublisher(SOCIAL_PLATFORMS.get("facebook", {})),
        "linkedin": LinkedInPublisher(SOCIAL_PLATFORMS.get("linkedin", {})),
        "instagram": InstagramPublisher(SOCIAL_PLATFORMS.get("instagram", {})),
        "zalo": ZaloPublisher(SOCIAL_PLATFORMS.get("zalo", {})),
    }
    
    results = {}
    for platform, content in generated_contents.items():
        if platform in publishers and content.platforms and platform in content.platforms:
            publisher = publishers[platform]
            result = publisher.publish(content.content, str(logo_path) if logo_path else None)
            results[platform] = result
            logger.info(f"{platform}: {'SUCCESS' if result.success else 'FAILED'} - {result.message}")
    
    # Step 5: Send emails
    logger.info("\n[5/5] Sending marketing emails...")
    email_sender = EmailSender(config)
    
    # Placeholder for email recipients (should be configurable)
    # In production, this would come from a database or config
    email_results = []
    
    # If contact_email is provided, send email to that address
    if contact_email:
        email_content = generated_contents.get("email")
        if email_content:
            result = email_sender.send_content_email(
                to_email=contact_email,
                content=email_content.content,
                subject=email_content.email_subject or email_content.subject,
                contact_email=contact_email
            )
            email_results.append(result)
            logger.info(f"Email sent to {contact_email}: {'SUCCESS' if result.success else 'FAILED'}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("PROCESS COMPLETED")
    logger.info("=" * 60)
    
    # Count successes
    success_count = sum(1 for r in results.values() if r.success)
    email_success = sum(1 for r in email_results if r.success)
    
    logger.info(f"Social posts: {success_count}/{len(results)} successful")
    logger.info(f"Emails: {email_success}/{len(email_results)} successful")
    logger.info(f"\nGenerated {len(generated_contents)} pieces of content")
    
    return {
        "social_results": results,
        "email_results": email_results,
        "generated_contents": generated_contents
    }


def run_interactive():
    """Run in interactive mode"""
    print("\n" + "=" * 60)
    print("EAVN Content Generator - Interactive Mode")
    print("=" * 60)
    
    print("\n[1] Generate content now (without publishing)")
    print("[2] Generate and publish to configured platforms")
    print("[3] Configure schedule")
    print("[4] Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        contact = input("Nhập email liên hệ (hoặc để trống): ").strip() or None
        generate_and_publish(contact_email=contact, test_mode=True)
    elif choice == "2":
        contact = input("Nhập email liên hệ (hoặc để trống): ").strip() or None
        generate_and_publish(contact_email=contact, test_mode=False)
    elif choice == "3":
        interval = input("Nhập khoảng thời gian (giờ, mặc định 72h): ").strip()
        if interval:
            # Update config
            global CONTENT_INTERVAL_HOURS
            CONTENT_INTERVAL_HOURS = int(interval)
        print(f"Schedule updated: every {CONTENT_INTERVAL_HOURS} hours")
    elif choice == "4":
        print("Goodbye!")
        sys.exit(0)


def run_scheduled():
    """Run in scheduled mode"""
    config = load_config()
    
    # Create scheduler
    scheduler = TaskScheduler(config)
    
    # Schedule the content job
    scheduler.schedule_content_job(
        job_func=lambda: generate_and_publish(),
        job_name="content_generation"
    )
    
    # Add daily summary job at preferred hour
    scheduler.schedule_daily_job(
        job_func=lambda: logger.info("Daily content generation check"),
        hour=config["PREFERRED_HOUR"],
        job_name="daily_check"
    )
    
    logger.info(f"\nScheduler running with {config['CONTENT_INTERVAL_HOURS']}h interval")
    logger.info(f"Preferred hour: {config['PREFERRED_HOUR']}:00")
    logger.info("Press Ctrl+C to stop")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        scheduler.stop()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="EAVN SocialMedia Content Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Interactive mode
  python main.py --scheduled              # Run scheduled background
  python main.py --generate --contact you@example.com  # Generate once
  python main.py --test                   # Test generate without publish
        """
    )
    
    parser.add_argument(
        "--scheduled", "-s",
        action="store_true",
        help="Run in scheduled mode (background)"
    )
    
    parser.add_argument(
        "--generate", "-g",
        action="store_true",
        help="Generate content once"
    )
    
    parser.add_argument(
        "--contact", "-c",
        type=str,
        help="Contact email for content CTA"
    )
    
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Test mode: generate without publishing"
    )
    
    parser.add_argument(
        "--platforms", "-p",
        nargs="+",
        choices=["facebook", "linkedin", "instagram", "zalo", "email"],
        help="Platforms to publish to"
    )
    
    args = parser.parse_args()
    
    # If scheduled mode, run scheduler
    if args.scheduled:
        run_scheduled()
        return
    
    # If generate mode
    if args.generate or args.test:
        platforms = args.platforms or ["facebook", "linkedin", "instagram", "email"]
        generate_and_publish(
            contact_email=args.contact,
            platforms=platforms,
            test_mode=args.test
        )
        return
    
    # Default: interactive mode
    run_interactive()


if __name__ == "__main__":
    main()
