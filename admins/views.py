from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Store
from accounts.decorators import admin_only 
from invoices.models import Invoice
from store.models import Product
from orders.models import Order

@login_required(login_url='accounts:log_in')
@admin_only
def dashboard(request):
    """عرض لوحة التحكم الخاصة بالادارة"""
    return render(request, 'admins/dashboard.html')

@login_required(login_url='accounts:log_in')
@admin_only
def show_stores(request):
    """عرض جميع المتاجر الخاضعة للإدارة  كما تحتوي على ألية البحث والفلترة"""
    stores = Store.objects.all()

    # ── فلترة ──────────────────────────────────────────
    status = request.GET.get('status')
    valid_statuses = [choice[0] for choice in Store.STATUS_CHOICES]
    if status in valid_statuses:
        stores = stores.filter(status=status)
        
    search = request.GET.get('search', '').strip()
    if search:
        filters = Q(name__icontains=search) | Q(phone_number1__icontains=search)
        stores = stores.filter(filters)
    # ── ترتيب ──────────────────────────────────────────
    VALID_SORTS = {
        '-created_at': '-created_at',   # الأحدث أولاً
        'created_at':  'created_at',    # الأقدم أولاً
        '-updated_at': '-updated_at',    # الأحدث تعديلاً أولاً
        'updated_at': 'updated_at',     # الأقدم تعديلاً أولاً
    }
    selected_sort = request.GET.get('sort', '-created_at')
    order_by = VALID_SORTS.get(selected_sort, '-created_at')
    stores = stores.order_by(order_by)
    # ── Pagination ──────────────────────────────────────
    paginator = Paginator(stores, 20)
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
        'selected_status': status or '',
        'search': search,
        'selected_sort':   selected_sort,
    }
    return render(request, 'admins/show_stores.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def store_list(request, sid):
    """عرض صفحة القائمة التي تحتوي على روابط الى تفاصيل المتجر و طلباته ومنتجاته و احصائياته"""
    store = get_object_or_404(Store, id=sid)
    context = {
        'store': store,
    }
    return render(request, 'admins/store_list.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def review_center(request):
    """عرض صفحة مركز المراجعات التي تحتوي على روابط و ملخص  لجميع المراجعات الواردة من المتاجر الخاضعة للإدارة"""
    stores = Store.objects.filter(status='pending').count()  # عدد المتاجر التي تنتظر المراجعة"
    products = Product.objects.filter(status='checking').count()  # عدد المنتجات التي تنتظر المراجعة"
    orders = Order.objects.filter(verification_status='checking').count()  # عدد الطلبات التي تنتظر المراجعة"
    invoices = Invoice.objects.filter(status="pending").count() # عدد الفواتير التي تنتظر الدفع"
    
    context = {
        'stores': stores,
        'products': products,
        'orders': orders,
        'invoices': invoices,
    }
    return render(request, 'admins/review_center.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def stores_to_review(request):
    """عرض صفحة تحتوي على جميع المتاجر التي تنتظر المراجعة"""
    stores = Store.objects.filter(status='pending').order_by('-updated_at')
    # ── فلترة ──────────────────────────────────────────
    search = request.GET.get('search', '').strip()
    if search:
        filters = Q(name__icontains=search) | Q(phone_number1__icontains=search)
        stores = stores.filter(filters)
    # ── ترتيب ──────────────────────────────────────────
    VALID_SORTS = {
        '-created_at': '-created_at',   # الأحدث أولاً
        'created_at':  'created_at',    # الأقدم أولاً
        '-updated_at': '-updated_at',    # الأحدث تعديلاً أولاً
        'updated_at': 'updated_at',     # الأقدم تعديلاً أولاً
    }
    selected_sort = request.GET.get('sort', '-created_at')
    order_by = VALID_SORTS.get(selected_sort, '-created_at')
    stores = stores.order_by(order_by)
    # ── Pagination ──────────────────────────────────────
    paginator = Paginator(stores, 20)
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
        'search': search,
        'selected_sort':   selected_sort,
    }
    return render(request, 'admins/stores_to_review.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def products_to_review(request):
    """عرض صفحة تحتوي على جميع المنتجات التي تنتظر المراجعة"""
    
    products = Product.objects.filter(status='checking').order_by('-updated_at')
    # ── فلترة ──────────────────────────────────────────

    search = request.GET.get('search', '').strip()
    if search:
        products = products.filter(name__icontains=search)
    # ── ترتيب ──────────────────────────────────────────
    VALID_SORTS = {
        '-upload_at': '-upload_at',   # الأحدث أولاً
        'upload_at':  'upload_at',    # الأقدم أولاً
        '-updated_at': '-updated_at',    # الأحدث تعديلاً أولاً
        'updated_at': 'updated_at',     # الأقدم تعديلاً أولاً
    }
    selected_sort = request.GET.get('sort', '-upload_at')
    order_by = VALID_SORTS.get(selected_sort, '-upload_at')
    products = products.order_by(order_by)
    # ── Pagination ──────────────────────────────────────
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number if page_number else 1)
    except Exception:
        page_obj = paginator.page(1)

    # ── نبني query string بدون page لاستخدامه في روابط الباجنيتور ──
    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_string = query_params.urlencode()  # مثال: status=approved&gender=male

    context = {
        'page_obj': page_obj,
        'query_string': query_string,
        'search': search,
        'selected_sort':   selected_sort,
    }
    return render(request, 'admins/products_to_review.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def orders_to_review(request):
    """عرض صفحة تحتوي على جميع الطلبات التي تنتظر المراجعة"""
    orders = Order.objects.filter(verification_status='checking').order_by('-updated_at')
    # ── فلترة ──────────────────────────────────────────

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
        'page_obj': page_obj,
        'query_string': query_string,
        'search': search,
        'selected_sort':   selected_sort,
    }
    return render(request, 'admins/orders_to_review.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def invoices_to_review(request):
    """عرض صفحة تحتوي على جميع الفواتير التي تنتظر الدفع"""
    invoices = Invoice.objects.filter(status='pending').order_by('-created_at')
    # ── فلترة ──────────────────────────────────────────

    search = request.GET.get('search', '').strip()
    if search:
        filters = Q(invoice_number__contains=search)

        invoices = invoices.filter(filters)

    # ── ترتيب ──────────────────────────────────────────
    VALID_SORTS = {
        '-created_at': '-created_at',   # الأحدث أولاً
        'created_at':  'created_at',    # الأقدم أولاً
    }
    selected_sort = request.GET.get('sort', '-created_at')
    order_by = VALID_SORTS.get(selected_sort, '-created_at')
    invoices = invoices.order_by(order_by)
    # ── Pagination ──────────────────────────────────────
    paginator = Paginator(invoices, 20)
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
        'search': search,
        'selected_sort':   selected_sort,
    }
    return render(request, 'admins/invoices_to_review.html', context)
