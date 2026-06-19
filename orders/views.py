from urllib import request

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.views.decorators.http import require_POST
import json

from orders.models import *
from orders.forms import *
from accounts.decorators import vendor_only 
from accounts.validators import get_user_type 
from accounts.models import Store

@login_required(login_url='accounts:log_in')
def show_orders(request, sid):
    """دالة عرض جميع الطلبات الخاصة بالمستخدم كما تحتوي على ألية البحث والفلترة """
    store = get_object_or_404(Store, id=sid)
    
    user_type = get_user_type(request.user)
    # تحقق ان كان المستخدم بائع ان المتجر الذي يريد تعديله هو متجره
    if user_type == 'vendor' and store.owner != request.user: # لو البائع يحاول الوصول لمتجر ليس له علاقة به
        raise Http404("المتجر غير موجود") 
    
    orders =  store.orders.exclude(verification_status="checking") # جلب جميع الطلبات بإستثناء التي لم يتم التحقق منها بعد

    # ── فلترة ──────────────────────────────────────────
    status = request.GET.get('status')
    if status in ['processing', 'delivered', 'canceled']:
        orders = orders.filter(status=status)
        
        
    verification_status = request.GET.get('verification_status')
    if verification_status in ['approved', 'rejected']:
        orders = orders.filter(verification_status=verification_status)


    search = request.GET.get('search', '').strip()
    if search:
        filters = Q(customer_name__icontains=search)

        if search.isdigit():
            filters |= Q(serial_number=int(search)) | Q(customer_phone__icontains=search)

        orders = orders.filter(filters)
    # ── ترتيب ──────────────────────────────────────────
    VALID_SORTS = {
        '-order_date': '-order_date',   # الأحدث أولاً
        'order_date':  'order_date',    # الأقدم أولاً
        '-updated_at': '-updated_at',    # الأحدث تعديلاً أولاً
        'updated_at': 'updated_at',     # الأقدم تعديلاً أولاً
    }
    selected_sort = request.GET.get('sort', '-order_date')
    order_by = VALID_SORTS.get(selected_sort, '-order_date')
    orders = orders.order_by(order_by)
    # ── Pagination ──────────────────────────────────────
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number if page_number else 1)
    except Exception:
        page_obj = paginator.page(1)

    # ── نبني query string بدون page لاستخدامه في روابط الباجنيتور ──
    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_string = query_params.urlencode()  

    context = {
        'sid': store.id,
        'page_obj': page_obj,
        'query_string': query_string,
        # قيم الفلاتر للحفاظ عليها في الـ form
        'selected_status': status or '',
        'selected_verification_status': verification_status or '',
        'search': search,
        'selected_sort':   selected_sort,
    }
    return render(request, 'orders/show_orders.html', context)

@login_required(login_url='accounts:log_in')
@vendor_only
def add_order_manually(request):
    """صفحة إنشاء طلب يدوي عن طريق صاحب المتجر"""
    store = request.user.userprofile.store
    
    order_form = OrderRegisterForm(store=store, is_vendor=True)
    item_form = OrderItemRegisterForm(store=store)
    
    query = request.GET.get("q", "").strip()
    
    products = store.products.filter(
        status="approved", 
        is_visible=True
    ).prefetch_related("colors__sizes")
    
    if query:
        products = products.filter(name__icontains=query)
    else:
        # عرض أحدث 10 منتجات فقط عند عدم وجود بحث
        products = products.order_by("-upload_at")[:10]
    
    
    for product in products:
        product.available_colors = [
            color for color in product.colors.all()
            if color.available
        ]

    context = {
        "order_form": order_form,
        "item_form": item_form,
        "products": products,
        "query": query,
    }
    return render(request, "orders/add_order_manually.html", context)

# هذه الدالة لاتتطلب تسجيل دخول لأنها مخصصة للزبائن
@require_POST
def add_order(request):
    """ الدالة المسؤولة عن انشاء طلب عن طريق كل من الزبون او البائع  """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({
            "success": False,
            "message": "صيغة البيانات المرسلة غير صحيحة.",
        }, status=400)

    customer_data = {
        "customer_name": data.get("customer_name", ""),
        "customer_phone": data.get("customer_phone", ""),
        "customer_location": data.get("customer_location", ""),
        "note": data.get("note", ""),
    }
    items_data = data.get("items", [])
    # التحقق أن المستخدم بائع 
    is_vendor = (
        request.user.is_authenticated and
        hasattr(request.user, 'userprofile') and
        request.user.userprofile.user_type == 'vendor'
    )
    order_form = OrderRegisterForm(customer_data, is_vendor=is_vendor)
    item_forms = []
    item_errors = {}

    if not isinstance(items_data, list) or not items_data:
        item_errors["__all__"] = ["السلة فارغة."]
        items_data = []

    for index, item in enumerate(items_data):
        form_data = {
            "product": item.get("product_id", ""),
            "product_color": item.get("color_id", ""),
            "product_size": item.get("size_id", ""),
            "qty": item.get("qty", ""),
        }
        item_form = OrderItemRegisterForm(form_data)
        item_forms.append(item_form)
        if not item_form.is_valid():
            item_errors[str(index)] = {
                field: [str(error) for error in errors]
                for field, errors in item_form.errors.items()
            }

    form_is_valid = order_form.is_valid()
    items_are_valid = not item_errors

    if form_is_valid and items_are_valid:
        products = [item_form.cleaned_data["product"] for item_form in item_forms]
        store = products[0].store

        if any(product.store_id != store.id for product in products):
            return JsonResponse({
                "success": False,
                "message": "لا يمكن إنشاء طلب يحتوي على منتجات من أكثر من متجر.",
                "errors": {},
                "item_errors": {"__all__": ["منتجات السلة يجب أن تكون من نفس المتجر."]},
            })

        with transaction.atomic():
            order = order_form.save(commit=False)
            order.store = store
            order.serial_number = order.create_serial_number()
            order.free_delivery = products[0].free_delivery
            # التحقق أن المستخدم بائع في هذا المتجر تحديداً
            is_store_vendor = (
                request.user.is_authenticated and
                hasattr(request.user, 'userprofile') and
                request.user.userprofile.user_type == 'vendor'
            )
            if is_store_vendor: # اذا كان منشئ الطلب بائع بالمتجر الطلب حقيقي تلقائيا
                order.verification_status = "approved"
            else: # إذا كان زبون → تحقق من إعداد المتجر
                order.verification_status = "checking" if store.check_orders else "approved"
            order.save()

            for item_form in item_forms:
                item_form.save(order=order)

        return JsonResponse({
            "success": True,
            "message": "شكرا لك، تم إرسال طلبك بنجاح.",
            "order_id": order.id,
            "serial_number": order.serial_number,
        })

    return JsonResponse({
        "success": False,
        "message": "يرجى تصحيح البيانات وإعادة إرسال الطلب.",
        "errors": {
            field: [str(error) for error in errors]
            for field, errors in order_form.errors.items()
        },
        "item_errors": item_errors,
    })
    
@login_required(login_url='accounts:log_in')
def edit_order(request, oid):
    """الدالة المسؤولة عن صفحة التعديل الخاصة بالطلب والتي تسمح للبائع بتعديل الطلبات التي في حالة  معالجة فقط"""
    user_type = get_user_type(request.user)
    order = get_object_or_404(Order, id=oid)
    items = order.items.all()
        
    # تحقق ان المستخدم بائع وان المنتج الذي يريد تعديله تابع لمتجره
    if  user_type == 'vendor' and request.user.userprofile.store != order.store :
        raise Http404("الطلب غير موجود")
    
    if request.method == "POST":
        if order.status != "processing" and  user_type == 'vendor': # لايمكن للبائعين تعديل الطلبات التي تم تسليمها او الغائها
            messages.error(request, "لايمكن تعديل الطلبات المستلمة او الملغية!")
            return redirect("orders:edit_order", oid=order.id)
        
        if user_type == "admin":    
            form = OrderAdminEditForm(request.POST, instance=order)
        else:
            form = OrderEditForm(request.POST, instance=order)
            
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل الطلب بنجاح")
            return redirect("orders:edit_order", oid=order.id)
    else:
        if user_type == "admin":
            form = OrderAdminEditForm(instance=order)
        else:
            form = OrderEditForm(instance=order)
            
    can_edit = not (
        # لو المنتج تم تسليمه او بعد التحقق طلع وهمي لاتعطي البائع صلاحية التعديل  
        # لو المستخدم اداري مهما كانت حالة الطلب اسمح له دائما بالتعديل
        user_type == "vendor"
        and (order.status != "processing" or order.verification_status == "rejected")
    )
        
    context = {
        "order": order,
        "edit_form": form,
        "can_edit": can_edit,
        "items": items
    }
    return render(request, 'orders/edit_order.html', context)
