from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from accounts.forms import *
from accounts.validators import validate_username, get_redirect_url_for_user,  get_user_type 
from accounts.decorators import vendor_only 

@login_required(login_url='accounts:log_in') 
@vendor_only
def account_details(request):
    """
    الدالة المسؤولة عن عرض الصفحة التي  تحتوي على بيانات الحساب الخاص بالبائع 
    يمكن فقط للبائعين الدخول اليها 
    """
    userprofile = request.user.userprofile
    
    context = {
        'userprofile': userprofile,
    }
    return render(request, 'accounts/account_details.html', context)

@login_required(login_url='accounts:log_in') 
@vendor_only
@require_POST
def edit_account_details(request):
    """
    الدالة المسؤولة عن تعديل بيانات الحساب الخاص بالبائع 
    يمكن فقط للبائعين الدخول اليها 
    """
    
    username = request.POST.get('username')
    name = request.POST.get('name')
    
    user = request.user
    current_user_id = request.user.pk if request.user.is_authenticated else None
    try:
        validate_username(username, current_user_id)
    except ValidationError as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })

    user.username = username
    userprofile = request.user.userprofile
    userprofile.name = name
    
    user.save()
    userprofile.save()
    return JsonResponse({
        "status": "success",
        "message": "تم التعديل بنجاح",
        "name": userprofile.name,
        "username": user.username
    })

@login_required(login_url='accounts:log_in')
def store_details(request, sid):
    # عرض بيانات المتجر أو حفظ جميع تعديلاته من نموذج واحد
    store = get_object_or_404(Store, id=sid)

    user_type = get_user_type(request.user)

    # منع البائع من الوصول إلى متجر ليس تابعًا له
    if user_type == 'vendor' and store.owner != request.user:
        raise Http404("المتجر غير موجود")

    if request.method == "POST":

        if user_type == "admin":
            form = StoreAdminUpdateForm(
                request.POST,
                request.FILES,
                instance=store
            )
        else:
            form = StoreUpdateForm(
                request.POST,
                request.FILES,
                instance=store
            )

        if form.is_valid():
            form.save()

            return JsonResponse({
                "status": "success",
                "message": "تم حفظ تعديلات المتجر بنجاح",

                "name": store.name,
                "location": store.location,
                "store_status": store.get_status_display(),
                "check_orders": store.get_check_orders_display(),

                "facebook": store.facebook,
                "instagram": store.instagram,
                "tiktok": store.tiktok,

                "phone_number1": store.phone_number1,
                "telegram": store.telegram,

                "logo_url": store.logo.url if store.logo else "",
            })

        errors = {
            field: [str(error) for error in error_list]
            for field, error_list in form.errors.items()
        }

        return JsonResponse({
            "status": "error",
            "errors": errors
        })

    # GET
    if user_type == "admin":
        form = StoreAdminUpdateForm(instance=store)
    else:
        form = StoreUpdateForm(instance=store)

    context = {
        "store": store,
        "form": form,
        "USER_TYPE": user_type,
    }

    return render(
        request,
        "accounts/store_details.html",
        context
    )

def sign_up(request):
    """الدالة المسؤولة عن صفحة انشاء حساب جديد للبائعين"""

    # لو المستخدم مسجل دخوله بالفعل جيب الرابط المناسب وقم بتحويله اليه
    if request.user.is_authenticated:
        redirect_url = get_redirect_url_for_user(request.user)
        return redirect(redirect_url or 'landing_page')
        
    
    if request.method == 'POST':
        form = StoreRegisterForm(request.POST)
        if form.is_valid():
            form.save() 
            # بعد ما يتم انشاء الحساب، يتم تحويله لصفحة تحت المراجعة لانتظار تفعيل الحساب من قبل الادارة
            return redirect('accounts:account_under_review')
    else:
        form = StoreRegisterForm()
        
    context = {
        'form': form,
    }
    return render(request, 'accounts/sign_up.html', context)

def check_username(request):
    """دالة التحقق من اليوزرنيم بشكل مباشر عند انشاء حساب"""
    
    username = request.GET.get('username')
    current_user_id = request.GET.get('current_user_id')        
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        current_user_id = None

    try:
        validate_username(username, current_user_id)
    except ValidationError as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })

    return JsonResponse({
        "status": "success",
        "message": "متاح"
    })

def check_phone_number(request):
    """
    دالة التحقق من رقم الهاتف بشكل مباشر
    يتم استدعائها من خلال جافاسكربت عند انشاء حساب جديد اوانشاء طلب سواء كان طلب يدوي او من خلال زبون
    """
    
    phone_number = request.GET.get('phone_number')

    try:
        validate_phone_number(phone_number)
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })

    return JsonResponse({
        "status": "success",
        "message": "رقم الهاتف صالح"
    })

def log_in(request): 
    """الدالة المسؤولة عن صفحة تسجيل الدخول لكل من الادارة و اللبائعين"""

    # لو المستخدم مسجل دخوله بالفعل جيب الرابط المناسب وقم بتحويله اليه
    if request.user.is_authenticated:
        redirect_url = get_redirect_url_for_user(request.user)
        return redirect(redirect_url or 'landing_page')
    
    form = LoginForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data.get('username'),
            password= form.cleaned_data.get('password')
            )
        if user:                
            redirect_url = get_redirect_url_for_user(user)
            # لو المتجر الخاص بالبائع قيد المراجعة لا تقم بتسجيل دخوله وحوله مباشرة للرابط المناسب
            if redirect_url == 'accounts:account_under_review':
                return redirect(redirect_url)
            
            login(request, user)
            return redirect(redirect_url or 'landing_page')
            
        form.add_error(None, "اسم المستخدم أو كلمة المرور غير صحيحة")
            
    context = {
        'form': form,
    }
    return render(request, 'accounts/log_in.html', context)

def log_out(request):
    '''
    الدالة المسؤولة عن آلية تسجيل الخروج 
    لايوجد صفحة لها تعمل عند استدعائها من الصفحة الخاصة بالحساب  
    بعد تأكيد تسجيل الخروج يتم تسجيل خروج المستخدم وتحويله لصفحة اللاند
    #change-later عدل الوصف بس تخلص مساواة الدالة
    '''
    if request.user.is_authenticated: 
        logout(request)
        return redirect('landing_page')
    else:
        return JsonResponse({
            "status": "error",
            "message": "المستخدم لم يقم بتسجيل الدخول بعد"
        })
    
def account_under_review(request):
    """الدالة المسؤولة عن صفحة تحت المراجعة لانتظار تفعيل الحساب من قبل الادارة"""
    
    if request.user.is_authenticated:
        if request.user.vendor.store.status != 'pending': # لو الشخص مسجل دخول بالفعل و حساب الشخص مو قيد المراجعة حوله لقائمة حسابه
            return redirect('accounts:account_list')
    else: 
        return render(request, 'accounts/account_under_review.html')