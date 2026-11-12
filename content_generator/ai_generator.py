"""
AI Content Generator - Generates professional content using AI
"""
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import google-generativeai, fallback to mock if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Using mock generator.")

try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


@dataclass
class GeneratedContent:
    """Result from AI content generation"""
    content: str
    subject: str
    hashtags: list[str]
    platforms: list[str]
    generated_at: str
    email_subject: Optional[str] = None
    email_body: Optional[str] = None


class AIGenerator:
    """
    AI-powered content generator
    Supports Gemini (Google) and Ollama (local) models
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.provider = config.get("AI_MODEL_PROVIDER", "gemini")
        
        # Style configuration
        self.language = config.get("CONTENT_STYLE", {}).get("language", "vi")
        self.tone = config.get("CONTENT_STYLE", {}).get("tone", "professional")
        
        # Initialize the generator
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the AI model"""
        if self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            logger.warning(f"Unknown provider: {self.provider}. Using mock.")
            self.model = self._create_mock_model()
    
    def _init_gemini(self):
        """Initialize Gemini model"""
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini not available. Using mock generator.")
            self.model = self._create_mock_model()
            return
        
        api_key = self.config.get("GEMINI_API_KEY", "")
        if not api_key:
            logger.warning("Gemini API key not set. Using mock generator.")
            self.model = self._create_mock_model()
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
            logger.info("Gemini model initialized")
        except Exception as e:
            logger.error(f"Error initializing Gemini: {e}")
            self.model = self._create_mock_model()
    
    def _init_ollama(self):
        """Initialize Ollama local model"""
        if not OLLAMA_AVAILABLE:
            logger.warning("Ollama not available. Using mock generator.")
            self.model = self._create_mock_model()
            return
        
        try:
            base_url = self.config.get("OLLAMA_BASE_URL", "http://localhost:11434")
            model_name = self.config.get("OLLAMA_MODEL", "qwen2.5:7b")
            
            # Check if Ollama is running
            response = requests.post(
                f"{base_url}/api/generate",
                json={"model": model_name, "prompt": "test", "stream": False}
            )
            
            if response.status_code == 200:
                self.model = {"base_url": base_url, "model": model_name}
                logger.info(f"Ollama model {model_name} initialized")
            else:
                raise Exception("Ollama not responding")
                
        except Exception as e:
            logger.error(f"Error initializing Ollama: {e}")
            self.model = self._create_mock_model()
    
    def _create_mock_model(self):
        """Create a mock model for testing"""
        return {
            "type": "mock",
            "name": "Mock Generator"
        }
    
    def generate_content(
        self,
        topic: str,
        source_content: str,
        platform: str = "facebook",
        include_logo: bool = True,
        contact_email: Optional[str] = None
    ) -> GeneratedContent:
        """
        Generate content for a specific platform
        
        Args:
            topic: The topic to write about
            source_content: Source material to reference
            platform: Target platform (facebook, linkedin, instagram, zalo, email)
            include_logo: Whether to include logo reference
            contact_email: Contact email for CTA
        """
        logger.info(f"Generating {platform} content for topic: {topic[:50]}...")
        
        # Build the prompt
        prompt = self._build_prompt(topic, source_content, platform, contact_email)
        
        # Generate content
        if self.provider == "gemini" and hasattr(self.model, 'generate_content'):
            result = self.model.generate_content(prompt)
            raw_content = result.text
        elif self.provider == "ollama" and isinstance(self.model, dict):
            raw_content = self._generate_ollama(prompt)
        else:
            # Mock generation
            raw_content = self._mock_generate(topic, platform)
        
        # Parse and format the content
        return self._parse_content(
            raw_content, platform, include_logo, contact_email
        )
    
    def _build_prompt(
        self,
        topic: str,
        source_content: str,
        platform: str,
        contact_email: Optional[str]
    ) -> str:
        """Build the AI prompt for content generation"""
        
        # Platform-specific instructions
        platform_instructions = {
            "facebook": """
                - Viết style Facebook: thân thiện, engaging, phù hợp mạng xã hội
                - Dùng emoji phù hợp (1-3 emoji)
                - Dùng hashtags ở cuối
                - Nhiệmatsch dài 200-400 từ
            """,
            "linkedin": """
                - Viết style LinkedIn: chuyên nghiệp, phù hợp B2B
                - Nhấn mạnh vào giải pháp doanh nghiệp
                - Nhiệmatsch dài 300-500 từ
                - Ít emoji hơn
            """,
            "instagram": """
                - Viết style Instagram: visual, ngắn gọn
                - Dùng nhiều emoji, hashtags
                - Nhiệmatsch ngắn 100-200 từ
                - Thích hợp kèm hình
            """,
            "zalo": """
                - Viết style Zalo: ngắn gọn, súc tích
                - Phù hợp nhắn tin nhóm/Zalo OA
                - Nhiệmatsch ngắn 50-150 từ
            """,
            "email": """
                - Viết style email marketing: chuyên nghiệp, chào hỏi
                - Có tiêu đề (subject) hấp dẫn
                - Content thân email
                - Có CTA (call to action) rõ ràng
            """
        }
        
        instructions = platform_instructions.get(platform, platform_instructions["facebook"])
        
        # Contact info
        contact_info = ""
        if contact_email:
            contact_info = f"\n\nThông tin liên hệ: {contact_email}\nHãy kèm theo email này trong CTA."
        
        prompt = f"""
        Bạn là trợ lý marketing chuyên nghiệp cho công ty EAVN (Eastern Access Vietnam).
        
        VỊ TRÍ: Content marketing specialist
        NGÔN NGỮ: Tiếng Việt chuyên nghiệp, rõ rang, không sáo rỗng, tôn trọng khách hàng
        PHONG CÁCH: Professional, informative, solution-oriented
        
        ĐỀ TÀI: {topic}
        
        NGUỒN THAM KHẢO:
        {source_content[:1500]}
        
        NỘI DUNG CẦN TẠO:
        - Content chuẩn cho nền tảng {platform}.{instructions}
        - Tập trung vào giải pháp cho doanh nghiệp
        - Khớp với sản phẩm liên quan: Lưu trữ dữ liệu (HDD, SSD, NAS, Cloud Storage)
        - Hiển thị logo EAVN cho mỗi bài đăng
        - Nếu có email liên hệ, đưa vào CTA{content_info}
        
        YÊU CẦU:
        - Tiếng Việt tự nhiên, chuyên nghiệp
        - Không dùng từ ngữ quá khách sáo
        - Cung cấp giá trị thực cho doanh nghiệp đọc
        - Có thông tin liên hệ/actionable
        - Kèm hashtag (nếu platform hỗ trợ)
        
        HỨA TĨM: Chỉ trả về content, không giải thích thêm.
        """
        
        return prompt
    
    def _generate_ollama(self, prompt: str) -> str:
        """Generate content using Ollama"""
        import requests
        
        base_url = self.model["base_url"]
        model = self.model["model"]
        
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "-system": "Bạn là trợ lý marketing của EAVN, viết content tiếng Việt chuyên nghiệp."
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"Ollama error: {response.status_code}")
    
    def _mock_generate(self, topic: str, platform: str) -> str:
        """Generate mock content for testing without AI"""
        templates = {
            "facebook": f"""
            🚀 Giải Pháp Mới Cho Doanh Nghiệp: {topic}

            Bạn đang tìm giải pháp lưu trữ dữ liệu hiệu quả? EAVN mang đến những giải pháp tiên tiến nhất hiện nay!

            💡 {topic} - Lựa chọn thông minh cho doanh nghiệp của bạn.

            Liên hệ ngay để được tư vấn:
            📧 [Email liên hệ]
            🌐 eascs.com.vn

            #EAVN #GiảiPhápDoanhNghiệp #CôngNghệ #Storage #DataSolution
            """.strip(),
            
            "linkedin": f"""
            📊 Giải Pháp Doanh Nghiệp: {topic}

            Trong bối cảnh chuyển đổi số mạnh mẽ, việc lựa chọn giải pháp lưu trữ dữ liệu phù hợp là yếu tố then chốt cho sự phát triển bền vững của doanh nghiệp.

            EAVN cung cấp các giải pháp lưu trữ tiên tiến từ Toshiba, Synology, Wasabi Cloud Storage và更多...

            ✅ Ưu điểm:
            - Hiệu suất cao, độ tin cậy
            - Tối ưu chi phí
            - Dễ dàng mở rộng
            - Hỗ trợ kỹ thuật 24/7

            Liên hệ EAVN để được tư vấn giải pháp phù hợp nhất với doanh nghiệp bạn!

            📧 Liên hệ: [Email liên hệ]
            🌐: eascs.com.vn
            """.strip(),
            
            "instagram": f"""
            🔥 Mở Đông Giải Pháp Lưu Trữ Hiện Đại!

            {topic} - Giải pháp thông minh cho dữ liệu doanh nghiệp.

            EAVN - Your trusted IT partner! ✨

            📩 Liên hệ: [Email liên hệ]

            #EAVN #TechVietnamese #StorageSolution #DataStorage #DoanhNghiệp
            """.strip(),
            
            "zalo": f"""
            📌 {topic}

            Giải pháp lưu trữ hiệu quả cho doanh nghiệp bạn.

            Liên hệ EAVN:
            📧 [Email liên hệ]
            🌐 eascs.com.vn
            """.strip(),
            
            "email": f"""
            SUBJECT: Giải Pháp Mới: {topic} Cho Doanh Nghiệp Của Bạn

            Kính gửi Quý Khách Hàng,

            Chào bạn, đây là thông tin về giải pháp mới nhất mà EAVN đang cung cấp:

            {topic}

            EAVN tin rằng giải pháp này sẽ mang lại giá trị thực cho doanh nghiệp của bạn. Với sự đồng hành của Toshiba, Synology, Wasabi và các đối tác hàng đầu, chúng tôi cam kết mang đến những giải pháp lưu trữ dữ liệu hiệu quả nhất.

            📞 Liên Hệ:
            Email: [Email liên hệ]
            Website: eascs.com.vn

            Trân trọng,
            EAVN Team
            """.strip()
        }
        
        return templates.get(platform, templates["facebook"])
    
    def _parse_content(
        self,
        raw_content: str,
        platform: str,
        include_logo: bool,
        contact_email: Optional[str]
    ) -> GeneratedContent:
        """Parse and structure the generated content"""
        
        now = __import__('datetime').datetime.now().isoformat()
        
        # Split content into parts
        parts = raw_content.split("\n\n")
        
        # Extract subject (first line if email)
        subject = ""
        email_body = raw_content
        hashtags = []
        
        if platform == "email":
            # Try to extract subject from content
            for line in parts:
                if line.upper().startswith("SUBJECT:"):
                    subject = line.replace("SUBJECT:", "").strip()
                    email_body = raw_content.replace(line, "").strip()
                    break
        else:
            # Extract hashtags from content
            for part in parts:
                if part.startswith("#"):
                    hashtags.extend(
                        [tag.strip() for tag in part.replace("\n", " ").split("#") if tag.strip()]
                    )
        
        # Ensure logo note
        if include_logo and platform != "email":
            raw_content += "\n\n[Logo EAVN]"
        
        return GeneratedContent(
            content=raw_content,
            subject=subject or f"Giải Pháp Mới: {topic[:30]}",
            hashtags=hashtags[:10] if hashtags else self._get_default_hashtags(platform),
            platforms=[platform],
            generated_at=now,
            email_subject=subject or f"[EAVN] Giải Pháp {topic[:40]}",
            email_body=email_body if platform == "email" else None
        )
    
    def _get_default_hashtags(self, platform: str) -> list[str]:
        """Get default hashtags for platform"""
        base_hashtags = [
            "#EAVN", "#EasternAccessVietnam", "#CongNghe",
            "#DoanhNghiep", "#DataSolution"
        ]
        
        if platform == "instagram":
            return base_hashtags + ["#Storage", "#NAS", "#CloudStorage"]
        elif platform == "facebook":
            return base_hashtags + ["#GiảiPháp", "#Toshiba", "#Synology"]
        elif platform == "linkedin":
            return base_hashtags + ["#Enterprise", "#BusinessSolution"]
        elif platform == "zalo":
            return ["#EAVN", "#Doanh nghiệp"]
        
        return base_hashtags
