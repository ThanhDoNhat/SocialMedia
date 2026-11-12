"""
SMTP Email Sender - Sends email marketing content via SMTP
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EmailResult:
    """Result of email sending operation"""
    success: bool
    to_email: str
    subject: str
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = ""

class SMTPPSender:
    """SMTP email sender with support for attachments, HTML, and images"""
    
    def __init__(self, config: dict):
        """
        Initialize SMTP sender
        
        Args:
            config: SMTP configuration dictionary
        """
        self.config = config
        self.smtp_server = config.get("smtp_server", "")
        self.smtp_port = config.get("smtp_port", 587)
        self.use_tls = config.get("use_tls", True)
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.sender_email = config.get("sender_email", "")
        self.sender_name = config.get("sender_name", "EAVN")
        self.reply_to = config.get("default_reply_to", self.sender_email)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        cc: Optional[List[str]] = None,
        reply_to: Optional[str] = None
    ) -> EmailResult:
        """
        Send an email
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            attachments: List of file paths to attach
            cc: CC recipients
            reply_to: Reply-to email (overrides default)
        """
        try:
            # Validate configuration
            if not self.smtp_server:
                logger.error("SMTP server not configured")
                return EmailResult(
                    success=False,
                    to_email=to_email,
                    subject=subject,
                    error="SMTP server not configured",
                    timestamp=__import__('datetime').datetime.now().isoformat()
                )
            
            if not self.sender_email:
                logger.error("Sender email not configured")
                return EmailResult(
                    success=False,
                    to_email=to_email,
                    subject=subject,
                    error="Sender email not configured",
                    timestamp=__import__('datetime').datetime.now().isoformat()
                )
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = self._format_address(self.sender_email, self.sender_name)
            msg["To"] = to_email
            
            if cc:
                msg["CC"] = ", ".join(cc)
            
            msg["Subject"] = subject
            
            if reply_to:
                msg["Reply-To"] = reply_to
            elif self.reply_to:
                msg["Reply-To"] = self.reply_to
            
            # Attach plain text
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            # Attach HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, "html", "utf-8"))
            
            # Attach logo if exists
            logo_path = Path(__file__).parent.parent / "assets" / "logo_eavn.png"
            if logo_path.exists():
                try:
                    with open(logo_path, "rb") as f:
                        logo = MIMEImage(f.read(), _subtype="png")
                        logo.add_header("Content-ID", "<logo_eavn>")
                        logo.add_header("Content-Disposition", "inline", filename="logo_eavn.png")
                        msg.attach(logo)
                except Exception as e:
                    logger.warning(f"Could not attach logo: {e}")
            
            # Attach files
            if attachments:
                for attachment_path in attachments:
                    path = Path(attachment_path)
                    if path.exists():
                        try:
                            with open(path, "rb") as f:
                                part = MIMEBase("application", "octet-stream")
                                part.set_payload(f.read())
                                encoders.encode_base64(part)
                                part.add_header(
                                    "Content-Disposition",
                                    f"attachment; filename={path.name}"
                                )
                                msg.attach(part)
                        except Exception as e:
                            logger.warning(f"Could not attach {attachment_path}: {e}")
            
            # Connect to SMTP server
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            server.ehlo()
            
            # Login if credentials provided
            if self.username and self.password:
                server.login(self.username, self.password)
            
            # Send email
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            
            server.sendmail(self.sender_email, recipients, msg.as_string())
            server.quit()
            
            logger.info(f"Email sent to {to_email}: {subject}")
            
            return EmailResult(
                success=True,
                to_email=to_email,
                subject=subject,
                message_id="sent",
                timestamp=__import__('datetime').datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return EmailResult(
                success=False,
                to_email=to_email,
                subject=subject,
                error=str(e),
                timestamp=__import__('datetime').datetime.now().isoformat()
            )
    
    def _format_address(self, email: str, name: str) -> str:
        """Format email address with display name"""
        # Simple format - for production, use email.headerregistry
        if name:
            return f"{name} <{email}>"
        return email


class EmailSender:
    """Email sender wrapper for content marketing"""
    
    def __init__(self, config: dict):
        self.smtp_config = config.get("SMTP_CONFIG", {})
        self.sender = SMTPPSender(self.smtp_config)
        self.include_contact_field = config.get("EMAIL_SETTINGS", {}).get(
            "include_contact_field", True
        )
    
    def send_content_email(
        self,
        to_email: str,
        content: str,
        subject: str,
        contact_email: Optional[str] = None
    ) -> EmailResult:
        """
        Send content marketing email
        
        Args:
            to_email: Recipient email
            content: Content body
            subject: Email subject
            contact_email: Optional contact email for CTA
        """
        # Add contact info if enabled
        if self.include_contact_field and contact_email:
            content += f"\n\n📧 Liên hệ: {contact_email}"
        elif self.include_contact_field:
            content += "\n\n📧 Liên hệ: [Điền email của bạn]"
        
        # Add EAVN signature
        content += """
            
---
EAVN - Eastern Access Vietnam
🌐 eascs.com.vn
"""
        
        return self.sender.send_email(
            to_email=to_email,
            subject=subject,
            body=content
        )
    
    def send_to_list(
        self,
        recipients: List[str],
        content: str,
        subject: str,
        contact_email: Optional[str] = None
    ) -> List[EmailResult]:
        """Send email to multiple recipients"""
        results = []
        
        for recipient in recipients:
            result = self.send_content_email(
                to_email=recipient,
                content=content,
                subject=subject,
                contact_email=contact_email
            )
            results.append(result)
        
        return results
