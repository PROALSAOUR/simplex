from django.shortcuts import redirect


def vendor_only(view_func):
    # طبقة حماية وظيفتها التحقق من ان نوع حساب المستخدم بائع
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