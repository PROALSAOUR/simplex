from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from accounts.models import Vendor
from accounts.forms import *
from accounts.validators import validate_username, get_redirect_url_for_user,  get_user_type 
from accounts.decorators import vendor_only 

@login_required(login_url='accounts:log_in') #تمنع الوصول تلقائيًا لأي مستخدم غير مسجل دخول، وتعيد توجيهه إلى صفحة التسجيل   
@vendor_only
def account_list(request):
    """
    الدالة المسؤولة عن عرض الصفحة التي  تحتوي على قائمة الصفحات الخاصة بالحساب 
    يمكن فقط للبائعين الدخول اليها 
    """
    context = {
        "store" : request.user.vendor.store
    }
    return render(request, 'accounts/account_list.html', context) 

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
@require_POST
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
            "message": "تم التعديل بنجاح",
            "name": vendor.name,
            "username": user.username
        })
        
    return JsonResponse({"status": "error", "message": "طلب غير صالح"})

@login_required(login_url='accounts:log_in')
def store_details(request, sid):
    """
    الدالة المسؤولة عن عرض الصفحة التي  تحتوي على بيانات المتجر المرتبط بالبائع 
    """
    store = get_object_or_404(Store, id=sid)
    user_type = get_user_type(request.user)
    # تحقق ان كان المستخدم بائع ان المتجر الذي يريد تعديله هو متجره
    if  user_type == 'vendor':
        if request.user.vendor.store != store : # لو البائع يحاول الوصول لمتجر ليس له علاقة به
            raise Http404("المتجر غير موجود")
        else: # لو المستخدم بائع و المتجر الذي يريد تعديله هو متجره تحقق من صلاحياته
            owner = True if  request.user.vendor.permission_level == "owner" else False
            
    else: # لو المستخدم اداري ليس لديه صلاحيات المطلقة الخاصة بالمالك
        owner = False
    
    employees = store.vendors.all() 
    employee_form = EmployeeRegisterForm()
    
    if user_type == "admin":
        store_basic_form = StoreAdminBasicForm(instance=store)
        store_social_form = StoreAdminSocialForm(instance=store)
    else:
        store_basic_form =  StoreBasicForm(instance=store)
        store_social_form = StoreSocialForm(instance=store)
        
    counts = employees.count()
    context = {
        'store': store,
        'owner': owner,
        'employees': employees,
        'employee_form': employee_form,
        'basic_form': store_basic_form,
        'social_form': store_social_form,
        'counts': counts,
    }
    return render(request, 'accounts/store_details.html', context)

@login_required(login_url='accounts:log_in')
@require_POST
def edit_store_basic(request, sid):
    """
    الدالة المسؤولة عن تعديل بيانات المتجر الاساسية وهي الاسم والموقع 
    """
    user_type = get_user_type(request.user)    
    # فحص الصلاحيات
    if user_type == 'vendor':
        # للبائع، التحقق من أنه مالك المتجر أو لديه صلاحيات متقدمة
        if request.user.vendor.permission_level not in ["owner", "full"]:
            return JsonResponse({
                "status": "error",
                "message": "عذراً, لا تمتلك الصلاحية لتنفيذ هذا الإجراء"
            }, status=403)

    store = get_object_or_404(Store, id=sid)
    if user_type == "admin":
        form = StoreAdminBasicForm(request.POST, instance=store)
    else:
        form =  StoreBasicForm(request.POST, instance=store)
    if form.is_valid():
        form.save()
        return JsonResponse({
            "status": "success",
            "message": "تم إجراء التعديل بنجاح",
            "name": store.name,
            "location": store.location,
            "store_status": store.get_status_display(),
            "check_orders": store.get_check_orders_display()
        })
    else:
        errors = {field: [str(error) for error in error_list] for field, error_list in form.errors.items()}
        return JsonResponse({"status": "error", "errors": errors})
        
@login_required(login_url='accounts:log_in')
@require_POST
def edit_store_social(request, sid):
    """
    الدالة المسؤولة عن تعديل حسابات المتجر الاجتماعية  
    """
    user_type = get_user_type(request.user)    
    # فحص الصلاحيات
    if user_type == 'vendor':
        # للبائع، التحقق من أنه مالك المتجر أو لديه صلاحيات متقدمة
        if request.user.vendor.permission_level not in ["owner", "full"]:
            return JsonResponse({
                "status": "error",
                "message": "عذراً, لا تمتلك الصلاحية لتنفيذ هذا الإجراء"
            }, status=403)

    store = get_object_or_404(Store, id=sid)
    if user_type == "admin":
        form = StoreAdminSocialForm(request.POST, instance=store)
    else:
        form =  StoreSocialForm(request.POST, instance=store)
    if form.is_valid():
        form.save()
        return JsonResponse({
            "status": "success",
            "message": "تم إجراء التعديل بنجاح",
            "telegram": store.telegram,
            "phone_number1": store.phone_number1,
            "facebook": store.facebook,
            "instagram": store.instagram,
            "tiktok": store.tiktok
        })
    else:
        errors = {field: [str(error) for error in error_list] for field, error_list in form.errors.items()}
        return JsonResponse({"status": "error", "errors": errors})

@login_required(login_url='accounts:log_in')
@require_POST
def edit_store_logo(request, sid):
    """
    الدالة المسؤولة عن تعديل لوجو المتجر  
    """
    user_type = get_user_type(request.user)    
    # فحص الصلاحيات
    if user_type == 'vendor':
        # للبائع، التحقق من أنه مالك المتجر أو لديه صلاحيات متقدمة
        if request.user.vendor.permission_level not in ["owner", "full"]:
            return JsonResponse({
                "status": "error",
                "message": "عذراً, لا تمتلك الصلاحية لتنفيذ هذا الإجراء"
            }, status=403)

    store = get_object_or_404(Store, id=sid)
    form = StoreLogoForm(request.POST, request.FILES, instance=store)
    if form.is_valid():
        form.save()
        return JsonResponse({
            "status": "success",
            "message": "تم تحديث لوجو المتجر بنجاح",
            "logo_url": store.logo.url
        })
    else:
        errors = {field: [str(error) for error in error_list] for field, error_list in form.errors.items()}
        return JsonResponse({"status": "error", "errors": errors})
        
@login_required(login_url='accounts:log_in')
@vendor_only
@require_POST
def add_employee(request):
    "دالة وظيفتها اضافة موظف جديد للمتجر, لايمكن الا لمالك المتجر "
    if request.method == "POST":
        if request.user.vendor.permission_level == 'owner':
            store = request.user.vendor.store 
            employee_number = store.vendors.count()    
            form = EmployeeRegisterForm(request.POST, store=store)
            if employee_number >= 5: # الحد الأقصى للموظفين لكل متجر هو 5
                return JsonResponse({
                    "status": "error",
                    "message": "لا يمكنك إضافة أكثر من 5 موظفين للمتجر"
                })
            try:
                if form.is_valid():
                    form.save()
                    return JsonResponse({"status": "success", "message": "تم اضافة الموظف بنجاح"})
                else:
                    return JsonResponse({"status": "error", "message": form.errors})
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)})

        else:
            return JsonResponse({
                "status": "error",
                "message": 'عذراً, يبدو انك لا تمتلك الصلاحية لإضافة موظف'
            })

    else:
        return JsonResponse({"status": "error", "message": "طلب غير صالح"})

@login_required(login_url='accounts:log_in')
@vendor_only
@require_POST
def remove_employee(request):
    "الدالة المسؤولة عن ازالة موظف من المتجر, لايمكن الا لمالك المتجر "
    if request.method == "POST":
        employee_id  = request.POST.get('employee_id')
        if request.user.vendor.permission_level == 'owner':
            try:
                employee_id = int(employee_id)
                employee = Vendor.objects.get(id=employee_id, store=request.user.vendor.store)
                user = employee.user # جيب  المستخدم واحذفه مشان ينحذف البائع والبروفايل المرتبطين فيه
                if employee.user.id == request.user.id: # منع المستخدم من حذف نفسه
                    return JsonResponse({
                        "status": "error",
                        "message": "لا يمكنك حذف نفسك."
                    })
                    
                user.delete()
                return JsonResponse({
                "status": "success",
                "message": 'تم حذف الموظف من المتجر بنجاح'
                })
            except Exception as e:
                return JsonResponse({
                "status": "error",
                "message": str(e)
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": 'عذراً, يبدو انك لا تمتلك الصلاحية لإزالة موظف'
            })
    else:
        return JsonResponse({"status": "error", "message": "طلب غير صالح"})
        
@login_required(login_url='accounts:log_in')
@vendor_only
@require_POST
def edit_employee(request):
    "الدالة المسؤولة عن تعديل صلاحيات موظف من المتجر, لايمكن الا لمالك المتجر "
    if request.method == "POST":
        employee_id  = request.POST.get('employee_id')
        new_permission_level = request.POST.get('permission_level')
        if request.user.vendor.permission_level == 'owner':
            try:
                employee_id = int(employee_id)
                employee = Vendor.objects.get(id=employee_id, store=request.user.vendor.store)
                if employee.user.id == request.user.id: # منع المستخدم من تعديل نفسه
                    return JsonResponse({
                        "status": "error",
                        "message": "لا يمكنك تعديل صلاحيات نفسك."
                    })
                else:
                    employee.permission_level = new_permission_level
                    employee.save()
                    return JsonResponse({
                    "status": "success",
                    "message": f'تم تعديل صلاحيات الموظف {employee.name}  بنجاح'
                    })
            except Exception as e:
                return JsonResponse({
                "status": "error",
                "message": str(e)
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": 'عذراً, يبدو انك لا تمتلك الصلاحية لتعديل الموظف'
            })
    else:
        return JsonResponse({"status": "error", "message": "طلب غير صالح"})

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
    
def account_under_review(request):
    """الدالة المسؤولة عن صفحة تحت المراجعة لانتظار تفعيل الحساب من قبل الادارة"""
    
    if request.user.is_authenticated:
        if request.user.vendor.store.status != 'pending': # لو الشخص مسجل دخول بالفعل و حساب الشخص مو قيد المراجعة حوله لقائمة حسابه
            return redirect('accounts:account_list')
    else: 
        return render(request, 'accounts/account_under_review.html')