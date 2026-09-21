from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q,F, ExpressionWrapper, DecimalField
from django.core.paginator import Paginator
from django.db import models as db_models
from accounts.models import Store
from accounts.decorators import admin_only 
from invoices.models import Invoice
from store.models import Product
from orders.models import Order

@login_required(login_url='accounts:log_in')
@admin_only
def dashboard(request):
    """عرض لوحة التحكم الخاصة بالادارة"""
    
    user_name = request.user.userprofile.name
    
    #  ملخص  لجميع المراجعات الواردة من المتاجر الخاضعة للإدارة
    stores_to_review = Store.objects.filter(status='pending').count()  # عدد المتاجر التي تنتظر المراجعة"
    products_to_review = Product.objects.filter(status='checking').count()  # عدد المنتجات التي تنتظر المراجعة"
    orders_to_review = Order.objects.filter(verification_status='checking').count()  # عدد الطلبات التي تنتظر التحقق"
    invoices_to_review = Invoice.objects.filter(status="pending").count() # عدد الفواتير التي تنتظر الدفع"
    
    context = {
        "user_name" : user_name,
        
        'stores_to_review': stores_to_review,
        'products_to_review': products_to_review,
        'orders_to_review': orders_to_review,
        'invoices_to_review': invoices_to_review,
    }
    return render(request, 'admins/dashboard.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def all_stores(request):
    """عرض جميع المتاجر الخاضعة للإدارة  كما تحتوي على ألية البحث والفلترة"""
    stores = Store.objects.all()
    has_stores = stores.exists()

    # ── فلترة ──────────────────────────────────────────
    status = request.GET.get('status')
    status_dict = dict(Store.STATUS_CHOICES)
    
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
        'name':       'name',         # أبجدياً تصاعدي
        '-name':      '-name',        # أبجدياً تنازلي
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
        'has_stores': has_stores,
        'page_obj': page_obj,
        'query_string': query_string,
        'selected_status': status or '',
        'selected_status_display': status_dict.get(status, status),
        'search': search,
        'selected_sort':   selected_sort,
    }
    return render(request, 'admins/all_stores.html', context)

@admin_only
@login_required(login_url='accounts:log_in')
def all_orders(request):
    """دالة عرض جميع الطلبات بالمنصة كما تحتوي على ألية البحث والفلترة """
        
    orders = Order.objects.all()
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
    valid_verification_status = [choice[0] for choice in Order.VERIFICATION_STATUS_CHOICES]
    if verification_status in valid_verification_status:
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
    return render(request, 'admins/all_orders.html', context)

@admin_only
@login_required(login_url='accounts:log_in')
def all_invoices(request):
    """
    عرض جميع الفواتير الخاصة بجميع المتاجر
    وهي صفحة خاصة بالإدارة فقط    
    """
    
    invoices = Invoice.objects.all()
    has_invoices = invoices.exists()
    
    invoices = invoices.annotate(
        final_value_db=ExpressionWrapper(
            F('commission_value') - F('discount'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )
    # ── فلترة ──────────────────────────────────────────
    status = request.GET.get('status')
    valid_statuses = [choice[0] for choice in Invoice.STATUS_CHOICES]
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
        '-updated_at':  '-updated_at',    # الأحدث تعديلا أولاً
        'updated_at':  'updated_at',    # الاقدم تعديلا أولاً
        '-paid_at': '-paid_at',   # الأحدث دفعاً أولاً
        'paid_at':  'paid_at',    # الأقدم دفعاً أولاً
        'final_value':    'final_value_db',   # الأرخص أولاً
        '-final_value':   '-final_value_db',  # الأغلى أولاً
    }
    selected_sort = request.GET.get('sort', '-updated_at')
    order_by = VALID_SORTS.get(selected_sort, '-updated_at')
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
        "has_invoices": has_invoices,
        'page_obj': page_obj,
        'query_string': query_string,
        # قيم الفلاتر للحفاظ عليها في الـ form
        'selected_status': status or '',
        'final_value_min': request.GET.get('final_value_min', ''),
        'final_value_max': request.GET.get('final_value_max', ''),
        'search': search,
        'selected_sort':   selected_sort,
    }
    
    return render(request, 'admins/all_invoices.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def all_products(request):
    """ صفحة تحتوي على جميع المنتجات """
    
    products = Product.objects.all()    
    has_products = products.exists()
    
    # ── تحويل الـ choices لقواميس (value -> label) لتسهيل الاستخدام ──
    status_dict = dict(Product.STATUS_CHOICES)
    type_dict = dict(Product.TYPE_CHOICES)
    gender_dict = dict(Product.GENDER_CHOICES)

    # ── فلترة ──────────────────────────────────────────
    status = request.GET.get('status')
    #change-later استبعد حالة قيد المراجعة من الخيارات كي لا يراها المستخدم
    valid_statuses = [choice[0] for choice in Product.STATUS_CHOICES]
    if status in valid_statuses:
        products = products.filter(status=status)

    product_type = request.GET.get('type')
    valid_types = [choice[0] for choice in Product.TYPE_CHOICES]
    if product_type in valid_types:
        products = products.filter(type=product_type)

    gender = request.GET.get('gender')
    valid_genders =  [choice[0] for choice in Product.GENDER_CHOICES]
    if gender in valid_genders:
        products = products.filter(gender=gender)

    is_visible = request.GET.get('is_visible')
    if is_visible == 'true':
        products = products.filter(is_visible=True)
    elif is_visible == 'false':
        products = products.filter(is_visible=False)

    offer = request.GET.get('offer')
    if offer == 'true':
        products = products.filter(offer=True)
    elif offer == 'false':
        products = products.filter(offer=False)

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    if price_min:
        try:
            products = products.filter(
                db_models.Q(offer=True, offer_price__gte=float(price_min)) |
                db_models.Q(offer=False, price__gte=float(price_min))
            )
        except ValueError:
            pass

    if price_max:
        try:
            products = products.filter(
                db_models.Q(offer=True, offer_price__lte=float(price_max)) |
                db_models.Q(offer=False, price__lte=float(price_max))
            )
        except ValueError:
            pass

    search = request.GET.get('search', '').strip()
    if search:
        products = products.filter(name__icontains=search)
    # ── ترتيب ──────────────────────────────────────────
    VALID_SORTS = {
        '-upload_at': '-upload_at',   # الأحدث أولاً
        'upload_at':  'upload_at',    # الأقدم أولاً
        '-updated_at': '-updated_at',    # الأحدث تعديلاً أولاً
        'updated_at': 'updated_at',     # الأقدم تعديلاً أولاً
        'name':       'name',         # أبجدياً تصاعدي
        '-name':      '-name',        # أبجدياً تنازلي
        'price':      'price',        # الأرخص أولاً
        '-price':     '-price',       # الأغلى أولاً
    }
    selected_sort = request.GET.get('sort', '-upload_at')
    order_by = VALID_SORTS.get(selected_sort, '-upload_at')
    products = products.order_by(order_by)
    # ── Pagination ──────────────────────────────────────
    paginator = Paginator(products, 12)
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
        "has_products": has_products,
        'page_obj': page_obj,
        'query_string': query_string,
        # قيم الفلاتر للحفاظ عليها في الـ form
        'selected_status': status or '',
        'selected_status_display': status_dict.get(status, status), 
        'selected_type': product_type or '',
        'selected_type_display': type_dict.get(product_type, product_type),
        'selected_gender': gender or '',
        'selected_gender_display': gender_dict.get(gender, gender),
        'selected_is_visible': is_visible or '',
        'selected_offer': offer or '',
        'price_min': request.GET.get('price_min', ''),
        'price_max': request.GET.get('price_max', ''),
        'search': search,
        'selected_sort':   selected_sort,
    }
    return render(request, 'admins/all_products.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def store_list(request, sid):
    """عرض صفحة القائمة التي تحتوي على روابط الى تفاصيل المتجر و طلباته ومنتجاته و احصائياته"""
    store = get_object_or_404(Store, id=sid)
    context = {
        'store': store,
    }
    return render(request, 'admins/store_list.html', context)

