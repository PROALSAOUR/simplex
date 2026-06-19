def global_data(request):
    """
    تتحقق من تسجيل المستخدم للدخول ثم تتحق من نوعه هل اداري ام بائع 
    """
    
    return {
        "STORE_ID": (
            request.user.userprofile.store.id
            if request.user.is_authenticated
            and hasattr(request.user, 'userprofile')
            and request.user.userprofile.user_type == 'vendor'
            and request.user.userprofile.store
            else None
        ),

        "USER_TYPE": (
            request.user.userprofile.user_type
            if request.user.is_authenticated
            and hasattr(request.user, 'userprofile')
            else None
        ),
    }
