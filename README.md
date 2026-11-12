# SocialMedia Content Generator - EAVN

Chương trình AI tự động tạo content chuyên nghiệp để gửi Email Digital Marketing và đăng mạng xã hội.

## Các tính năng

- **AI Content Generation**: Tạo content tiếng Việt chuyên nghiệp từ nhiều nguồn
- **Nguồn content**: Website sản phẩm, nguồn nội bộ, online news
- **Social Media**: Facebook, LinkedIn, Instagram, Zalo
- **Email Marketing**: Gửi qua SMTP với logo EAVN
- **Schedule**: Đặt lịch tự động (mặc định 3 ngày 1 lần)
- **Logo EAVN**: Hiển thị trong mọi bài đăng và email

## Cấu trúc dự án

```
SocialMedia/
├── config/
│   └── settings.py          # Cấu hình toàn cục
├── content_sources/
│   ├── __init__.py
│   ├── website_scraper.py   # Scraping website sản phẩm
│   ├── online_news.py       # Tìm tin công nghệ online
│   └── source_manager.py    # Quản lý các nguồn
├── content_generator/
│   ├── __init__.py
│   ├── ai_generator.py      # Gọi AI model sinh content
│   └── templates.py         # Template content
├── scheduler/
│   ├── __init__.py
│   └── task_scheduler.py    # Lên lịch chạy tự động
├── social_platforms/
│   ├── __init__.py
│   ├── facebook.py
│   ├── linkedin.py
│   ├── instagram.py
│   └── zalo.py
├── email_sender/
│   ├── __init__.py
│   └── smtp_sender.py       # Gửi email qua SMTP
├── assets/
│   └── logo_eavn.png        # Logo công ty (upload từ James)
├── utils/
│   ├── __init__.py
│   └── helpers.py           # Hàm hỗ trợ
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
└── README.md
```

## Cài đặt

### 1. Cài dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình

Copy `config/settings.example.py` thành `config/settings.py` và điền thông tin:

```bash
cp config/settings.example.py config/settings.py
```

### 3. Upload logo

Đặt file logo vào thư mục `assets/logo_eavn.png`

### 4. Chạy chương trình

```bash
python main.py
```

## Cấu hình AI Model

### Google Gemini (Free tier)

Đăng ký tại https://aistudio.google.com/ để lấy API key, sau đó thiết lập:

```bash
export GEMINI_API_KEY=your_api_key_here
```

### Local Ollama (Optional)

Cài Ollama: https://ollama.ai/
```bash
ollama pull qwen2.5:7b
```

## Schedule

Mặc định: 3 ngày 1 lần. Có thể thay đổi trong `config/settings.py`.

## Social Platforms

- **Facebook**: Sử dụng Graph API hoặc Meta Business Suite
- **LinkedIn**: Sử dụng LinkedIn API
- **Instagram**: Sử dụng Instagram Graph API
- **Zalo**: Sử dụng Zalo OA API

*Lưu ý: Cần đăng ký developer account cho từng platform để lấy API credentials.*

## Gửi Email

Sử dụng SMTP với thông tin được cấu hình trong `config/settings.py`.
