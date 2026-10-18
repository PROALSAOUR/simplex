def global_data(request):
    """
    تتحقق من تسجيل المستخدم للدخول ثم تتحق من نوعه هل اداري ام بائع 
    """
    
    # القيم الافتراضية. 
    store_id = None 
    store_name = None 
    store_logo = None 
    user_type = None
    
    # التحقق من تسجيل الدخول. 
    if request.user.is_authenticated: 
        # جلب الملف الشخصي مرة واحدة. 
        profile = getattr(request.user, 'userprofile', None) 
        if profile: 
            user_type = profile.user_type 
            # جلب بيانات المتجر للبائع فقط. 
            if user_type == 'vendor': 
                store = profile.store 
                if store: 
                    store_id = store.id 
                    store_name = store.name 
                    store_logo = store.logo.url if store.logo else None 
                    
    return { 
        'STORE_ID': store_id, 
        'STORE_NAME': store_name, 
        'STORE_LOGO': store_logo, 
        'USER_TYPE': user_type, 
    }
    
    
