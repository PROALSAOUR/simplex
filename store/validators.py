import imghdr

def validate_image_file(image_file, max_size_mb=10, allowed_types=None):
    """
    تتحقق من:
    - حجم الصورة
    - نوع الصورة الحقيقي (وليس الاسم)

    ترجع:
    True  -> إذا الصورة صالحة
    False -> إذا غير صالحة
    """

    if allowed_types is None:
        allowed_types = ["jpeg", "png", "webp", "jpg"]

    # 🚨 1. التحقق من الحجم
    size_mb = image_file.size / (1024 * 1024)
    if size_mb > max_size_mb:
        return False

    # 🚨 2. التحقق من النوع الحقيقي
    image_file.seek(0)
    file_type = imghdr.what(image_file)

    # إعادة المؤشر للبداية
    image_file.seek(0)

    if file_type not in allowed_types:
        return False

    return True