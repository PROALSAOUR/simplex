from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models as db_models
from django.db.models import Q, Sum ,F, ExpressionWrapper, DecimalField
from django.utils.timezone import now
from accounts.models import Store
from accounts.validators import get_user_type 
from accounts.decorators import admin_only 
from management.models import calculate_commission, Recipe
from store.models import Product
from orders.models import Order

@login_required(login_url='accounts:log_in')
@admin_only
def admins_dashboard(request):
    """عرض لوحة التحكم الخاصة بالادارة"""
    return render(request, 'management/dashboard.html')

@login_required(login_url='accounts:log_in')
@admin_only
def show_stores(request):
    """عرض جميع المتاجر الخاضعة للإدارة  كما تحتوي على ألية البحث والفلترة"""
    stores = Store.objects.all()

    # ── فلترة ──────────────────────────────────────────
    status = request.GET.get('status')
    if status in ['pending', 'active', 'inactive']:
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
    return render(request, 'management/show_stores.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def store_list(request, sid):
    """عرض صفحة القائمة التي تحتوي على روابط الى تفاصيل المتجر و طلباته ومنتجاته و احصائياته"""
    store = get_object_or_404(Store, id=sid)
    context = {
        'store': store,
    }
    return render(request, 'management/store_list.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def review_center(request):
    """عرض صفحة مركز المراجعات التي تحتوي على روابط و ملخص  لجميع المراجعات الواردة من المتاجر الخاضعة للإدارة"""
    stores = Store.objects.filter(status='pending').count()  # عدد المتاجر التي تنتظر المراجعة"
    products = Product.objects.filter(status='checking').count()  # عدد المنتجات التي تنتظر المراجعة"
    orders = Order.objects.filter(verification_status='checking').count()  # عدد الطلبات التي تنتظر المراجعة"
    invoices = Recipe.objects.filter(status="pending").count() # عدد الفواتير التي تنتظر الدفع"
    
    context = {
        'stores': stores,
        'products': products,
        'orders': orders,
        'invoices': invoices,
    }
    return render(request, 'management/review_center.html', context)

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
    return render(request, 'management/stores_to_review.html', context)

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
    return render(request, 'management/products_to_review.html', context)

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
    return render(request, 'management/orders_to_review.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def invoices_to_review(request):
    """عرض صفحة تحتوي على جميع الفواتير التي تنتظر الدفع"""
    invoices = Recipe.objects.filter(status='pending').order_by('-created_at')
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
    return render(request, 'management/invoices_to_review.html', context)

@login_required(login_url='accounts:log_in')
def invoice_details(request, rid):
    """الدالة المسؤولة عن صفحة عرض تفاصيل الفاتورة"""
    
    invoice = get_object_or_404(Recipe, id=rid)
    
    store = invoice.store
    
    user_type = get_user_type(request.user)    
    # تحقق ان كان المستخدم بائع ان المتجر الذي يريد عرض فاتورته هو متجره
    if user_type == 'vendor' and store.owner != request.user: # لو البائع يحاول الوصول لفاتورة متجر ليس له علاقة به
        raise Http404("الفاتورة غير موجودة")
    
    invoice_orders = invoice.orders.all
    
    context = {
        'store': store,
        'invoice':invoice,
        'orders':invoice_orders,
    }
    
    return render(request, 'management/invoice_details.html', context)
    

@login_required(login_url='accounts:log_in')
def store_billing(request, store_id):
    """
    عرض جميع الفواتير الخاصة بالمتجر
    بالإضافة الى عرض المبلغ المستحق هذا الشهر حتى الأن
    
    """
    store = get_object_or_404(Store, id=store_id)
    user_type = get_user_type(request.user)    
    # تحقق ان كان المستخدم بائع ان المتجر الذي يريد عرض احصائياته هو متجره
    if user_type == 'vendor' and store.owner != request.user: # لو البائع يحاول الوصول لمتجر ليس له علاقة به
        raise Http404("المتجر غير موجود")
    
    invoices = store.invoices.all
    
    total_sales = (
        store.orders.filter(
            status='delivered',
            verification_status='approved',
            delivery_date__year=now().year,
            delivery_date__month=now().month
        ).aggregate(
            total=Sum('total_selling_price')
        )['total'] or 0
    )
    commission = calculate_commission(total_sales)
    
    context = {
        'store': store,
        'invoices': invoices,
        'total_sales': total_sales,
        'commission': commission,
    }
    return render(request, 'management/store_billing.html', context)

@admin_only
@login_required(login_url='accounts:log_in')
def billing_management(request):
    """
    عرض جميع الفواتير الخاصة بجميع المتاجر
    وهي صفحة خاصة بالإدارة فقط    
    """
    
    invoices = Recipe.objects.all()
    invoices = invoices.annotate(
        final_value_db=ExpressionWrapper(
            F('commission_value') - F('discount'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )
    # ── فلترة ──────────────────────────────────────────
    status = request.GET.get('status')
    valid_statuses = [choice[0] for choice in Recipe.STATUS_CHOICES]
    if status in valid_statuses :
        invoices = invoices.filter(status=status)

    final_value_min = request.GET.get('final_value_min')
    final_value_max = request.GET.get('final_value_max')

    if final_value_min:
        try:
            invoices = invoices.filter(
                db_models.Q(final_value_db__gte=float(final_value_min))
            )
        except ValueError:
            pass

    if final_value_max:
        try:
            invoices = invoices.filter(
                db_models.Q(final_value_db__lte=float(final_value_max))
            )
        except ValueError:
            pass

    search = request.GET.get('search', '').strip()
    if search:
        invoices = invoices.filter( 
            Q(invoice_number__icontains=search) |
            Q(store__name__icontains=search)
        )
    # ── ترتيب ──────────────────────────────────────────
    VALID_SORTS = {
        '-created_at': '-created_at',   # الأحدث أولاً
        'created_at':  'created_at',    # الأقدم أولاً
        '-paid_at': '-paid_at',   # الأحدث دفعاً أولاً
        'paid_at':  'paid_at',    # الأقدم دفعاً أولاً
        'final_value':    'final_value_db',        # الأرخص أولاً
        '-final_value':   '-final_value_db',       # الأغلى أولاً
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

    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_string = query_params.urlencode()  

    context = {
        'page_obj': page_obj,
        'query_string': query_string,
        # قيم الفلاتر للحفاظ عليها في الـ form
        'selected_status': status or '',
        'final_value_min': request.GET.get('final_value_min', ''),
        'final_value_max': request.GET.get('final_value_max', ''),
        'search': search,
        'selected_sort':   selected_sort,
    }
    
    return render(request, 'management/billing_management.html', context)

@login_required(login_url='accounts:log_in')
def store_statistics(request, store_id):
    """
    عرض صفحة الاحصائيات الخاصة بالمتجر    
    """
    store = get_object_or_404(Store, id=store_id)
    user_type = get_user_type(request.user)    
    # تحقق ان كان المستخدم بائع ان المتجر الذي يريد عرض احصائياته هو متجره
    if user_type == 'vendor' and store.owner != request.user: # لو البائع يحاول الوصول لمتجر ليس له علاقة به
        raise Http404("المتجر غير موجود")
    
    context = {
        'store': store,
    }
    return render(request, 'management/store_statistics.html', context)