# Content Generator Settings
# Copy this file to settings.py and fill in your actual values

# ==================== AI MODEL CONFIG ====================
# Lựa chọn model: "gemini" hoặc "ollama"
AI_MODEL_PROVIDER = "gemini"  # "gemini" hoặc "ollama"

# Gemini API configuration
GEMINI_API_KEY = "AQ.Ab8RN6Jce5PEsGK6PFqeyJgTb3ICTTlTt0T9_GuuHxAlum2NNA"  # API key từ https://aistudio.google.com/

# Ollama local configuration (nếu dùng model local)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:7b"

# ==================== SCHEDULE CONFIG ====================
# Tần suất tạo content (giờ)
# Mặc định: 3 ngày 1 lần = 72 giờ
CONTENT_INTERVAL_HOURS = 72

# Thời gian chạy ưu tiên (giờ) - ví dụ 9h sáng
PREFERRED_HOUR = 9

# ==================== SOURCE CONFIG ====================
# Các website sản phẩm sẽ scraping
PRODUCT_WEBSITES = [
    "https://eascs.com.vn",
    "https://www.toshiba-storage.com",
    "https://www.aucore-tech.com",
    "https://wasabi.com",
    "https://www.synology.com",
]

# RSS feeds hoặc nguồn online news liên quan
ONLINE_SOURCES = [
    # Có thể thêm RSS feed của các trang tin công nghệ
    # Ví dụ: "https://tech.vn/rss",
]

# ==================== SOCIAL MEDIA CONFIG ====================
SOCIAL_PLATFORMS = {
    "facebook": {
        "enabled": True,
        "page_id": "",          # ID Facebook Page
        "access_token": "",     # Facebook Graph API token
        "api_version": "v18.0",
    },
    "linkedin": {
        "enabled": True,
        "company_id": "",       # LinkedIn Company ID
        "access_token": "",     # LinkedIn API token
        "api_version": "v2",
    },
    "instagram": {
        "enabled": True,
        "business_account_id": "",
        "access_token": "",
        "api_version": "v18.0",
    },
    "zalo": {
        "enabled": True,
        "oa_id": "",            # Zalo OA ID
        "access_token": "",
        "api_url": "https://open.zalo.me",
    },
}

# ==================== EMAIL/SMTP CONFIG ====================
SMTP_CONFIG = {
   "smtp_server": "mail.eascs.com.vn",        # Ví dụ: "smtp.office365.com" hoặc "smtp.gmail.com"
  "smtp_port": 465,         # 587 (TLS) hoặc 465 (SSL)
 "use_tls": True,
   "username": "thanh.do@eascs.com.vn",           # Email người gửi @eascs.com.vn
  "password": "Th@nh3010",           # Mật khẩu hoặc App Password
    "sender_email": "thanh.do@eascs.com.vn",       # Email gửi đi @eascs.com.vn
   "sender_name": "EAVN_Solution",    # Tên hiển thị
   "default_reply_to": "thanh.do@eascs.com.vn",   # Email reply mặc định
}

# ==================== CONTENT CONFIG ====================
# Email setting
EMAIL_SETTINGS = {
    "include_contact_field": True,  # Có trường email liên hệ để người dùng điền
    "default_subject_prefix": "[EAVN] ",  # Tiêu đề email mặc định
}

# Style content
CONTENT_STYLE = {
    "language": "vi",         # Tiếng Việt
    "tone": "professional",   # Chuyên nghiệp, rõ rang, tôn trọng khách hàng
    "include_logo": True,
    "include_contact": True,
}

# ==================== LOGGING ====================
LOG_FILE = "content_generator.log"
LOG_LEVEL = "INFO"
