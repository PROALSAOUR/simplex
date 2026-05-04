from PIL import Image
import io
from django.core.files.base import ContentFile


def compress_image(image_file, quality=85, max_width=1920):
    """
    ضغط الصورة وإرجاعها كـ ContentFile متوافق مع جانغو.
    
    Args:
        image_file: ملف الصورة القادم من request.FILES
        quality: جودة الصورة (1-95)
        max_width: أقصى عرض بالبكسل
    
    Returns:
        ContentFile: ملف جاهز للحفظ في ImageField
    """
    img = Image.open(image_file)

    # تحويل RGBA/P إلى RGB لدعم JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # تصغير الصورة مع الحفاظ على نسبة الأبعاد
    original_width, original_height = img.size
    if original_width > max_width:
        ratio = max_width / original_width
        new_height = int(original_height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # حفظ الصورة المضغوطة في الذاكرة
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=quality, optimize=True)
    output.seek(0)

    # استخراج اسم الملف الأصلي وتغيير امتداده إلى .jpg
    original_name = getattr(image_file, "name", "image.jpg")
    file_name = original_name.rsplit(".", 1)[0] + ".jpg"
    
    return ContentFile(output.read(), name=file_name)

    