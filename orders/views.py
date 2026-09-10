from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.db import transaction , models as db_models
from django.db.models import Q
from django.views.decorators.http import require_POST
import json

from orders.models import *
from orders.forms import *
from accounts.decorators import vendor_only 
from accounts.validators import get_user_type 
from accounts.models import Store

@login_required(login_url='accounts:log_in')
def store_orders(request, sid):
    """دالة عرض جميع الطلبات الخاصة بالمستخدم كما تحتوي على ألية البحث والفلترة """
    store = get_object_or_404(Store, id=sid)
    
    user_type = get_user_type(request.user)
    # تحقق ان كان المستخدم بائع ان المتجر الذي يريد تعديله هو متجره
    if user_type == 'vendor' and store.owner != request.user: # لو البائع يحاول الوصول لمتجر ليس له علاقة به
        raise Http404("المتجر غير موجود") 
    
    can_view_orders = True
    if user_type == 'vendor' and store.status == 'inactive': # لو البائع يريد عرض طلباته ومتجره غير مفعل
        can_view_orders = False
    
    orders =  store.orders.exclude(verification_status="checking") # جلب جميع الطلبات بإستثناء التي لم يتم التحقق منها بعد
    has_orders = orders.exists()

    # ── تحويل الـ choices لقواميس (value -> label) لتسهيل الاستخدام ──
    status_dict = dict(Order.STATUS_CHOICES)
    verification_status_dict = dict(Order.VERIFICATION_STATUS_CHOICES)

    # ── فلترة ──────────────────────────────────────────
    status = request.GET.get('status')
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if status in valid_statuses:
        orders = orders.filter(status=status)
        
        
    verification_status = request.GET.get('verification_status')
    if verification_status in ['approved', 'rejected']:
        orders = orders.filter(verification_status=verification_status)
        
    tvalue_min = request.GET.get('tvalue_min')
    tvalue_max = request.GET.get('tvalue_max')    
    if tvalue_min:
        try:
            orders = orders.filter(
                db_models.Q( total_selling_price__gte=float(tvalue_min))
            )
        except ValueError:
            pass

    if tvalue_max:
        try:
            orders = orders.filter(
                db_models.Q( total_selling_price__lte=float(tvalue_max))
            )
        except ValueError:
            pass


    search = request.GET.get('search', '').strip()
    if search:
        filters = Q(customer_name__icontains=search)

        if search.isdigit():
            filters |= Q(serial_number=int(search)) 

        orders = orders.filter(filters)
    # ── ترتيب ──────────────────────────────────────────
    VALID_SORTS = {
        '-order_date': '-order_date',   # الأحدث أولاً
        'order_date':  'order_date',    # الأقدم أولاً
        '-updated_at': '-updated_at',    # الأحدث تعديلاً أولاً
        'updated_at': 'updated_at',     # الأقدم تعديلاً أولاً
        'tvalue': 'total_selling_price',  # الأقل قيمة أولاً
        '-tvalue': '-total_selling_price', # الأعلى قيمة أولاً
    }
    selected_sort = request.GET.get('sort', '-order_date')
    order_by = VALID_SORTS.get(selected_sort, '-order_date')
    orders = orders.order_by(order_by)
    # ── Pagination ──────────────────────────────────────
    paginator = Paginator(orders, 12)
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
        'can_view_orders': can_view_orders,
        'has_orders': has_orders,
        'page_obj': page_obj,
        'query_string': query_string,
        # قيم الفلاتر للحفاظ عليها في الـ form
        'selected_status': status or '',
        'selected_status_display': status_dict.get(status, status), 
        'selected_verification_status': verification_status or '',
        'selected_verification_display': verification_status_dict.get(verification_status, verification_status),
        'search': search,
        'selected_sort':   selected_sort,
        'tvalue_min': request.GET.get('tvalue_min', ''),
        'tvalue_max': request.GET.get('tvalue_max', ''),
    }
    return render(request, 'orders/store_orders.html', context)

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
        "store": store,
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
def view_order(request, oid):
    """الدالة المسؤولة عن صفحة التعديل الخاصة بالطلب والتي تسمح للبائع بتعديل الطلبات التي في حالة  المعالجة فقط"""
    user_type = get_user_type(request.user)
    order = get_object_or_404(Order, id=oid)
    
    # تحقق من ملكية الطلب
    if user_type == "vendor":
        if request.user.userprofile.store != order.store:
            raise Http404("الطلب غير موجود")
        
    items = order.items.all()
    
   # البائع يستطيع التعديل فقط أثناء المعالجة
    can_edit = (
        user_type == "admin"
        or order.status == "processing"
    )
    
    # --------------------------------------------------
    # إنشاء الفورمين بشكل افتراضي
    # --------------------------------------------------

    customer_form = OrderEditCustomerForm(
        instance=order
    )

    if user_type == "admin":
        status_form = OrderAdminEditStatusForm(
            instance=order
        )
    else:
        status_form = OrderEditStatusForm(
            instance=order
        )
    
    # --------------------------------------------------
    # POST
    # --------------------------------------------------
    
    if request.method == "POST":
        
        form_type = request.POST.get("form_type")
        
        # ==============================================
        # تعديل بيانات الزبون
        # ==============================================
        if form_type == "customer":
            customer_form = OrderEditCustomerForm(
                request.POST,
                instance=order
            )

            if customer_form.is_valid():
                customer_form.save()

                messages.success(
                    request,
                    "تم تعديل بيانات الزبون بنجاح."
                )

                return redirect( "orders:view_order", oid=order.id)
            
        # ==============================================
        # تعديل حالة الطلب
        # ==============================================
        elif form_type == "status":

            if not can_edit:
                messages.error(
                    request,
                    "لا يمكن تعديل حالة الطلب المستلمة أو الملغاة."
                )

                return redirect( "orders:view_order", oid=order.id)

            if user_type == "admin":
                status_form = OrderAdminEditStatusForm(
                    request.POST,
                    instance=order
                )
            else:
                status_form = OrderEditStatusForm(
                    request.POST,
                    instance=order
                )

            if status_form.is_valid():
                status_form.save()

                messages.success(
                    request,
                    "تم تعديل حالة الطلب بنجاح."
                )

                return redirect( "orders:view_order", oid=order.id)

        else:
            messages.error(
                request,
                "طلب غير صالح."
            )

            return redirect(
                "orders:view_order",
                oid=order.id
            )
                     
    context = {
        "order": order,
        "customer_form": customer_form,
        "status_form": status_form,
        "can_edit": can_edit,
        "items": items,
    }
    return render(request, 'orders/view_order.html', context)

@login_required(login_url='accounts:log_in')
@require_POST
def add_order_item(request, oid):
    """إضافة عنصر جديد للطلب من داخل صفحة التعديل وتحديث إجماليات الطلب بدون إعادة تحميل الصفحة."""
    order = get_object_or_404(Order, id=oid)
    user_type = get_user_type(request.user)

    if user_type == 'vendor' and request.user.userprofile.store != order.store:
        raise Http404("الطلب غير موجود")

    if user_type == 'vendor' and (order.status != 'processing' or order.verification_status == 'rejected'):
        return JsonResponse({
            "success": False,
            "status": "failed",
            "message": "لايمكن تعديل الطلبات المستلمة او الملغية!",    
        })
                
    form_data = {
        "product": request.POST.get("product_id"),
        "product_color": request.POST.get("color_id"),
        "product_size": request.POST.get("size_id"),
        "qty": request.POST.get("quantity"),
    }

    form = OrderItemRegisterForm(
        form_data,
        store=order.store,
    )
    
    if not form.is_valid():
        return JsonResponse({
            "success": False,
            "status": "force",
            "message": "يرجى تصحيح البيانات.",
            "errors": {
                field: [str(error) for error in errors]
                for field, errors in form.errors.items()
            },
        })

    with transaction.atomic():
        order_item = form.save(order=order)
        order.calculate_totals()
        order.save(update_fields=[
            "total_purchase_price",
            "total_selling_price",
            "total_profit",
        ])

    return JsonResponse({
        "success": True,
        "status": "success",
        "message": "تمت إضافة المنتج إلى الطلب بنجاح.",

        "item": {
            "id": order_item.id,
            "product": order_item.product.name,
            "product_id": order_item.product.id,
            "color": order_item.color,
            "size": order_item.size,
            "qty": order_item.qty,
            "price": str(order_item.selling_price),
            "total": str(order_item.get_total_price()),
            "image": order_item.image.url if order_item.image else "",
        },
        "order_totals": {
            "selling": order.total_selling_price,
            "profit": order.total_profit,
            "purchase": order.total_purchase_price
        }
    })


@login_required(login_url='accounts:log_in')
@require_POST
def delete_order_item(request, item_id):
    """ 
    الدالة المسؤولة عن حذف عنصر من عناصر الطلب مع تحديث قيم الطلب بعد الحذف
    تعيد جيسون ريسبونس بالنجاح او الفشل 
    """

    item = get_object_or_404(OrderItem, id=item_id)
    order = item.order
    
    user_type = get_user_type(request.user)
    # تحقق ان المستخدم بائع وان المنتج الذي يريد تعديله تابع لمتجره
    if  user_type == 'vendor' and request.user.userprofile.store != order.store :
        raise Http404("الطلب غير موجود")
    
    if order.items.count() == 1:
        # منع حذف آخر منتج
        return JsonResponse({
            "success": False,
            "message": "لا يمكن حذف آخر منتج من الطلب. ",
        })
    
    item.delete()

    order.calculate_totals()

    order.save(update_fields=[
        "total_purchase_price",
        "total_selling_price",
        "total_profit",
    ])

    return JsonResponse({
        "success": True,
        "message": "تم حذف المنتج بنجاح.",
        "item_id": item_id,
        "order_totals": {
            "selling": order.total_selling_price,
            "profit": order.total_profit,
            "purchase": order.total_purchase_price
        }
    })
    
    