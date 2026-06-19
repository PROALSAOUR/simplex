from django.shortcuts import redirect
from django.http import JsonResponse
from functools import wraps

def vendor_only(view_func):
    """طبقة حماية وظيفتها التحقق من ان نوع حساب المستخدم بائع والا تعيد توجيهه لصفحة الهبوط الرئيسية"""
    def wrapper(request, *args, **kwargs):
        user = request.user

        if (
            hasattr(user, 'userprofile') and
            user.userprofile.user_type == 'vendor'
        ):
            return view_func(request, *args, **kwargs)

        return redirect('landing_page')  
    return wrapper

def admin_only(view_func):
    """طبقة حماية وظيفتها التحقق من ان نوع حساب المستخدم ادارة والا تعيد توجيهه لصفحة الهبوط الرئيسية"""
    def wrapper(request, *args, **kwargs):
        user = request.user

        if (
            hasattr(user, 'userprofile') and
            user.userprofile.user_type == 'admin'
        ):
            return view_func(request, *args, **kwargs)

        return redirect('landing_page')  
    return wrapper

