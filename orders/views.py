from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.db.models import Q


from orders.models import *
from orders.forms import *
from accounts.decorators import vendor_only 


@login_required(login_url='accounts:log_in')
@vendor_only
def show_orders(request):
    """دالة عرض جميع الطلبات الخاصة بالمستخدم كما تحتوي على ألية البحث والفلترة """
    vendor = request.user.vendor
    orders =  vendor.store.orders.exclude(verification_status="checking") # جلب جميع الطلبات بإستثناء التي لم يتم التحقق منها بعد

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
            filters |= Q(serial_number=int(search))

        orders = orders.filter(filters)
    # ── ترتيب ──────────────────────────────────────────
    VALID_SORTS = {
        '-order_date': '-order_date',   # الأحدث أولاً
        'order_date':  'order_date',    # الأقدم أولاً
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
    store = request.user.vendor.store

    if request.method == "POST":
        order_form = OrderRegisterForm(request.POST, store=store, is_vendor=True)
        item_form = OrderItemRegisterForm(request.POST, store=store)

        if order_form.is_valid() and item_form.is_valid():
            order_form.save(order_item_form=item_form)
            return redirect("orders:show_orders")
    else:
        order_form = OrderRegisterForm(store=store, is_vendor=True)
        item_form = OrderItemRegisterForm(store=store)

    context = {
        "order_form": order_form,
        "item_form": item_form,
    }
    return render(request, "orders/add_order_manually.html", context)

@login_required(login_url='accounts:log_in')
@vendor_only
def edit_order(request, oid):
    """الدالة المسؤولة عن صفحة التعديل الخاصة بالمنتج"""
    order = get_object_or_404(Order, id=oid)
        
    # تحقق ان المستخدم بائع وان المنتج الذي يريد تعديله تابع لمتجره
    if  request.user.userprofile.user_type == 'vendor':
        if request.user.vendor.store != order.store :
            raise Http404("الطلب غير موجود")
    
    if request.method == "POST":
        if order.status != "processing":
            messages.error(request, "لايمكن تعديل الطلبات المستلمة او الملغية!")
            return redirect("orders:edit_order", oid=order.id)
            
        form = OrderEditForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل الطلب بنجاح")
            return redirect("orders:edit_order", oid=order.id)
    else:
        form = OrderEditForm(instance=order)
        
    context = {
        "order": order,
        "edit_form": form,
    }
    return render(request, 'orders/edit_order.html', context)