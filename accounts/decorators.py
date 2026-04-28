from django.shortcuts import redirect
from django.http import JsonResponse
from functools import wraps

PERMISSIONS = {
    "basic": ["owner", "full", "edit"],   #  (العرض والتعديل) صلاحيات أساسية
    "advanced": ["owner", "full"],        # (العرض والتعديل والحذف) صلاحيات أقوى
}

def vendor_only(view_func):
    """طبقة حماية وظيفتها التحقق من ان نوع حساب المستخدم بائع والا تعيد توجيهه لصفحة الهبوط الرئيسية"""
    def wrapper(request, *args, **kwargs):
        user = request.user

        if (
            hasattr(user, 'userprofile') and
            user.userprofile.user_type == 'vendor' and
            hasattr(user, 'vendor')
        ):
            return view_func(request, *args, **kwargs)

        return redirect('landing_page')  
    return wrapper

def admin_only(view_func):
    # طبقة حماية وظيفتها التحقق من ان نوع حساب المستخدم ادارة
    pass

def advanced_permission_required():
    """طبقة حماية وظيفتها التحقق من ان صلاحيات المستخدم عالية وانه يستطيع التعديل والحذف"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.vendor.permission_level in PERMISSIONS["advanced"]:
                return view_func(request, *args, **kwargs)
            return JsonResponse({
                "status": "error",
                "message": "عذراً, لا تمتلك الصلاحية لتنفيذ هذا الإجراء"
            })
        return _wrapped_view
    return decorator

