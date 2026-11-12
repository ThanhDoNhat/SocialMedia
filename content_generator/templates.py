"""
Content Templates - Pre-defined templates for different content types
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class ContentTemplate:
    """A content template"""
    name: str
    platform: str
    template: str
    hashtags: list[str]

# Template dictionary
TEMPLATES = {
    "solution_intro": {
        "facebook": ContentTemplate(
            name="Giới thiệu giải pháp",
            platform="facebook",
            template="""
🚀 {topic_title}

Chào các bạn, hôm nay EAVN xin giới thiệu giải pháp mới: {topic_description}

📌 Ưu điểm nổi bật:
{benefits}

💼 Phù hợp cho: {target_audience}

Hãy liên hệ EAVN để được tư vấn chi tiết nhé!

📧 Liên hệ: [Email liên hệ]
🌐: eascs.com.vn

#EAVN #GiảiPhápDoanhNghiệp #CongNghe
            """.strip(),
            hashtags=["#EAVN", "#DoanhNghiep", "#CongNghe", "#Storage", "#DataSolution"]
        ),
        "linkedin": ContentTemplate(
            name="Giới thiệu giải pháp B2B",
            platform="linkedin",
            template="""
📊 {topic_title}

Trong bối cảnh doanh nghiệp cần chuyển đổi số, giải pháp {topic_name} từ EAVN mang lại:

✅ {benefits}

🎯 Đối tượng phù hợp: {target_audience}

EAVN - Đối tác chiến lược của bạn trong lĩnh vực lưu trữ dữ liệu và giải pháp công nghệ.

📧 Liên hệ tư vấn: [Email liên hệ]
🌐: eascs.com.vn
            """.strip(),
            hashtags=["#EAVN", "#Enterprise", "#BusinessSolution", "#DataStorage", "#IT"]
        ),
        "instagram": ContentTemplate(
            name="Post Instagram",
            platform="instagram",
            template="""
{topic_title} 🔥

{topic_description}

💡 {benefits_short}

Liên hệ EAVN ngay! 👇
📧 [Email liên hệ]
🌐 eascs.com.vn

#EAVN #TechVietnamese #StorageSolution
            """.strip(),
            hashtags=["#EAVN", "#TechVietnamese", "#StorageSolution", "#NAS", "#CloudStorage"]
        ),
        "zalo": ContentTemplate(
            name="Zalo OA message",
            platform="zalo",
            template="""
📌 {topic_title}

{topic_description}

👉 {benefits_short}

Liên hệ: [Email liên hệ]
            """.strip(),
            hashtags=["#EAVN"]
        ),
        "email": ContentTemplate(
            name="Email marketing",
            platform="email",
            template="""
SUBJECT: {subject_line}

Kính gửi Quý Khách Hàng,

Chào mừng quý khách đến với EAVN - Eastern Access Vietnam.

Hôm nay chúng tôi xin giới thiệu: {topic_title}

{topic_description}

✨ Điểm nổi bật:
{benefits}

🎯 Tại sao nên chọn EAVN?

- Chúng tôi hiểu rõ nhu cầu của doanh nghiệp Việt Nam
- Giải pháp tối ưu, giá cả hợp lý
- Hỗ trợ kỹ thuật tận tình
- Đối tác với các thương hiệu quốc tế uy tín

📞 Liên hệ ngay để được tư vấn:

Email: [Email liên hệ]
Website: eascs.com.vn

Trân trọng,
Team EAVN
            """.strip(),
            hashtags=[]
        )
    },
    "product_feature": {
        "facebook": ContentTemplate(
            name="Tạp chí sản phẩm",
            platform="facebook",
            template="""
✨ {product_name} - Giải Pháp Lưu Trữ Thông Minh

{product_description}

🔹 Đặc điểm nổi bật:
{features}

🔹 Ứng dụng: {use_cases}

EAVN cung cấp {product_name} với giá ưu đãi, hỗ trợ kỹ thuật trọn đời!

📧 Liên hệ: [Email liên hệ]
🌐: eascs.com.vn

#EAVN #Toshiba #Synology #Wasabi #Storage
            """.strip(),
            hashtags=["#EAVN", "#Toshiba", "#Synology", "#Wasabi", "#Storage", "#HardDrive", "#NAS"]
        ),
        "linkedin": ContentTemplate(
            name="Tạp chí sản phẩm B2B",
            platform="linkedin",
            template="""
💼 {product_name} - Giải Pháp Doanh Nghiệp

{product_description}

📌 Thông số kỹ thuật:
{features}

🏢 Ứng dụng thực tế:
{use_cases}

Liên hệ EAVN để triển khai giải pháp phù hợp với doanh nghiệp bạn.

📧 [Email liên hệ]
🌐 eascs.com.vn
            """.strip(),
            hashtags=["#EAVN", "#Enterprise", "#BusinessSolution", "#DataStorage", "#Synology"]
        ),
        "email": ContentTemplate(
            name="Email giới thiệu sản phẩm",
            platform="email",
            template="""
SUBJECT: Giới Thiệu {product_name} - Giải Pháp Mới Từ EAVN

Kính gửi Quý Khách Hàng,

EAVN tự hào giới thiệu {product_name} - giải pháp lưu trữ tiên tiến cho doanh nghiệp.

{product_description}

🔍 Đặc điểm nổi bật:
{features}

💼 Ứng dụng: {use_cases}

Với {product_name}, doanh nghiệp của bạn sẽ:
- Tối ưu chi phí lưu trữ
- Tăng hiệu suất làm việc
- Đảm bảo an toàn dữ liệu

📞 Liên hệ EAVN để đặt hàng hoặc được tư vấn:
📧 [Email liên hệ]
🌐 eascs.com.vn

Trân trọng,
EAVN Team
            """.strip(),
            hashtags=[]
        )
    }
}


def get_template(template_name: str, platform: str) -> Optional[ContentTemplate]:
    """Get a template for a specific platform"""
    templates = TEMPLATES.get(template_name, {})
    return templates.get(platform)


def list_templates() -> dict:
    """List all available templates"""
    return {name: {platform: t.name for platform, t in templates.items()} 
            for name, templates in TEMPLATES.items()}
