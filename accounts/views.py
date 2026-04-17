from os import name

from django.shortcuts import redirect, render
from .forms import EmployeeRegisterForm, VendorRegisterForm, LoginForm, EmployeeRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .validators import validate_username, get_redirect_url_for_user
from .decorators import vendor_only
from django.contrib.auth.decorators import login_required

    # تعديل بيانات المتجر
    # دالة اضافة مستخدمين للمتجر
    # دالة حذف مستخدمين من المتجر
    # دالة تعديل صلاحيات مستخدمين المتجر

@login_required(login_url='accounts:log_in') #تمنع الوصول تلقائيًا لأي مستخدم غير مسجل دخول، وتعيد توجيهه إلى صفحة التسجيل   
@vendor_only
def account_list(request):
    """
    الدالة المسؤولة عن عرض الصفحة التي  تحتوي على قائمة الصفحات الخاصة بالحساب 
    يمكن فقط للبائعين الدخول اليها 
    """
    return render(request, 'accounts/account_list.html')

@login_required(login_url='accounts:log_in') 
@vendor_only
def account_details(request):
    """
    الدالة المسؤولة عن عرض الصفحة التي  تحتوي على بيانات الحساب الخاص بالبائع 
    يمكن فقط للبائعين الدخول اليها 
    """
    vendor = request.user.vendor
    
    context = {
        'vendor': vendor,
    }
    return render(request, 'accounts/account_details.html', context)

@login_required(login_url='accounts:log_in') 
@vendor_only
def edit_account_details(request):
    """
    الدالة المسؤولة عن تعديل بيانات الحساب الخاص بالبائع 
    يمكن فقط للبائعين الدخول اليها 
    """
    
    if request.method == "POST":
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
        vendor = request.user.vendor
        vendor.name = name
        
        user.save()
        vendor.save()
        return JsonResponse({
            "status": "success",
            "message": "تم التعديل بنجاح"
        })
        
    return JsonResponse({"status": "error", "message": "طلب غير صالح"})

@login_required(login_url='accounts:log_in')
@vendor_only
def store_details(request):
    """
    الدالة المسؤولة عن عرض الصفحة التي  تحتوي على بيانات المتجر المرتبط بالبائع 
    يمكن فقط للبائعين الدخول اليها 
    """
    vendor = request.user.vendor
    store = vendor.store
    owner = True if vendor.permission_level == "full" else False
    employees = store.vendors.all() #change-later اعرض الموظفين جميعا بس اذا هو صلاحياته تحكم كامل حتى لو فيه مستخدم غير تحكم كامل لاتخليه يعدله او يحذفه
    
    context = {
        'store': store,
        'owner': owner,
        'employees': employees,
    }
    return render(request, 'accounts/store_details.html', context)

@login_required(login_url='accounts:log_in')
@vendor_only
def add_employee(request):
    # تحقق من صلاحية المستخدم
    if request.method == "POST":
        if request.user.vendor.permission_level == 'full':
            store = request.user.vendor.store 
            form = EmployeeRegisterForm(request.POST, store=store)
            if form.is_valid():
                form.save()
                return redirect("success_page")
    else:
        form = EmployeeRegisterForm(store=store)
    return render(request, "register_employee.html", {"form": form})



@login_required(login_url='accounts:log_in')
@vendor_only
def edit_store_details(request):
    pass










def sign_up(request):
    """الدالة المسؤولة عن صفحة انشاء حساب جديد للبائعين"""

    # لو المستخدم مسجل دخوله بالفعل جيب الرابط المناسب وقم بتحويله اليه
    if request.user.is_authenticated:
        redirect_url = get_redirect_url_for_user(request.user)
        return redirect(redirect_url or 'landing_page')
        
    
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
    # current_user_id = request.user.pk if request.user.is_authenticated else None
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
            "message": "المستخدم لم يقم بتسجيل الدخول اصلا"
        })
    
# change-later هي الصفحة بيقدر يشوفها الي حالة حسابه قيد المراجعة فقط ولايمكن لاي احد اخر عرضها
def account_under_review(request):
    """الدالة المسؤولة عن صفحة تحت المراجعة لانتظار تفعيل الحساب من قبل الادارة"""
    return render(request, 'accounts/account_under_review.html')