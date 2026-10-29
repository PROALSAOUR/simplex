import imghdr
from datetime import datetime, timedelta
from django.utils import timezone

BOT_KEYWORDS = ('bot', 'crawler', 'spider', 'slurp', 'facebookexternalhit')
VIEW_COOLDOWN = timedelta(minutes=10)

def is_bot(request):
    "دالة تتحقق ان المستخدم ليس بوتا بل شخص حقيقي"
    
    
    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    return not ua or any(k in ua for k in BOT_KEYWORDS)

def should_count_view(request, product_id):
    session_key = f'product_view_{product_id}'
    last_view = request.session.get(session_key)
    now = timezone.now()

    if last_view:
        try:
            last_view_time = datetime.fromisoformat(last_view)
            if timezone.is_naive(last_view_time):
                last_view_time = timezone.make_aware(last_view_time)
            if now - last_view_time < VIEW_COOLDOWN:
                return False
        except (ValueError, TypeError):
            pass

    request.session[session_key] = now.isoformat()
    return True

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