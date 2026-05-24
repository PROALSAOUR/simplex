from accounts.decorators import PERMISSIONS
def global_data(request):
    """
    تتحقق من تسجيل المستخدم للدخول ثم تتحق من نوعه هل اداري ام بائع 
    ان كان بائع تقوم بالحصول على مستوى صلاحياته وتمررها للقالب كما تمرر قائمة الصلاحيات المتقدمة ايضا
    """
    
    if request.user.is_authenticated and request.user.userprofile.user_type == 'vendor': # لازم يتم التحقق انه المستخدم مسجل دخول وانه بائع
        user_level = request.user.vendor.permission_level
    else:
        user_level = None
    return {
        "STORE_ID": getattr(request.user, 'vendor', None).store.id if request.user.is_authenticated and request.user.userprofile.user_type == 'vendor' else None,
        "USER_TYPE": request.user.userprofile.user_type if request.user.is_authenticated else None,
        "USER_LEVEL": user_level,
        "ADVANCED_PERMISSIONS": PERMISSIONS["advanced"],
    }
