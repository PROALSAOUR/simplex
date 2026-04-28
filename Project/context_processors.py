from accounts.decorators import PERMISSIONS
def global_data(request):
    """
    تتحقق من تسجيل المستخدم للدخول ثم تتحق من كونه بائع 
    ان كان كذلك تقوم بالحصول على مستوى صلاحياته وتمررها للقالب كما تمرر قائمة الصلاحيات المتقدمة ايضا
    """
    
    if request.user.is_authenticated and request.user.userprofile.user_type == 'vendor': # لازم يتم التحقق انه المستخدم مسجل دخول وانه بائع
        user_level = request.user.vendor.permission_level
    else:
        user_level = None
    return {
        "USER_LEVEL": user_level,
        "ADVANCED_PERMISSIONS": PERMISSIONS["advanced"],
    }
