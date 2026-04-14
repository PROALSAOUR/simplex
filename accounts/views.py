from django.shortcuts import redirect, render
from .forms import VendorRegisterForm, LoginForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .validators import validate_username

def main_accounts(request): #change-later
    return render(request, 'accounts/main_accounts_page.html')

def sign_up(request):
    """الدالة المسؤولة عن صفحة انشاء حساب جديد للبائعين"""
    # لو المستخدم مسجل دخوله بالفعل، يتم تحويله لصفحة تحت المراجعة لانتظار تفعيل الحساب من قبل الادارة
    if request.user.is_authenticated:
        return redirect('accounts:account_under_review') #change-later  قم بتحويله لصفحة لوحة تحكم البائع أو الادارة حسب نوعه او اي صفحة بتحددها بعدين
    
    if request.method == 'POST':
        form = VendorRegisterForm(request.POST)
        if form.is_valid():
            form.save() 
            # بعد ما يتم انشاء الحساب، يتم تحويله لصفحة تحت المراجعة لانتظار تفعيل الحساب من قبل الادارة
            return redirect('accounts:account_under_review')
    else:
        form = VendorRegisterForm()
        
    context = {
        'form': form,
    }
    return render(request, 'accounts/sign_up.html', context)

def check_username(request):
    """دالة التحقق من اليوزرنيم بشكل مباشر عند انشاء حساب"""
    
    username = request.GET.get('username')
    try:
        validate_username(username)
    except ValidationError as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })

    return JsonResponse({
        "status": "success",
        "message": "متاح"
    })

def log_in(request): 
    """الدالة المسؤولة عن صفحة تسجيل الدخول لكل من الادارة و اللبائعين"""
    # لو المستخدم مسجل دخوله بالفعل، يتم تحويله لصفحة تحت المراجعة لانتظار تفعيل الحساب من قبل الادارة
    if request.user.is_authenticated:
        return redirect('accounts:account_under_review') #change-later  قم بتحويله لصفحة لوحة تحكم البائع أو الادارة حسب نوعه او اي صفحة بتحددها بعدين
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:                
                user_profile = user.userprofile
                if user_profile.user_type == 'vendor':
                    store = user.vendor.store # تحقق من حالة المتجر المرتبط بالبائع
                    if store.status == 'pending': # يمنع تسجيل الدخول إذا كانت حالة المتجر قيد المراجعة
                        return redirect('accounts:account_under_review')
                    else:
                        login(request, user)
                        return redirect('vendors:vendor_dashboard')  # قم بتحويله لصفحة لوحة تحكم البائع
                elif user_profile.user_type == 'admin':
                    login(request, user)
                    return redirect('admin_dashboard')  # قم بتحويله لصفحة لوحة تحكم الادارة #change-later
            else:
                form.add_error(None, "اسم المستخدم أو كلمة المرور غير صحيحة")
        else:
            form = LoginForm()
    else:
        form =  LoginForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/log_in.html', context)

def log_out(request):
    '''
    الدالة المسؤولة عن آلية تسجيل الخروج 
    لايوجد صفحة لها تعمل عند استدعائها من الصفحة الخاصة بالحساب بواسطة جافاسكريبت
    بعد تأكيد تسجيل الخروج يتم تسجيل خروج المستخدم وتحويله لصفحة اللاند
    #change-later عدل الوصف بس تخلص مساواة الدالة
    '''
    pass

def account_under_review(request):
    """الدالة المسؤولة عن صفحة تحت المراجعة لانتظار تفعيل الحساب من قبل الادارة"""
    return render(request, 'accounts/account_under_review.html')