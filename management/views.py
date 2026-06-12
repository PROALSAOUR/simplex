from django.shortcuts import render, get_object_or_404
from accounts.decorators import admin_only 
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from accounts.models import Store
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
        filters = Q(name__icontains=search) | Q(slug__icontains=search) 
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
    
    context = {
        'stores': stores,
        'products': products,
        'orders': orders,
    }
    return render(request, 'management/review_center.html', context)

#change-later ضيف  صفحة عرض لكل متجر او طلب او منتج يجب مراجعته
@login_required(login_url='accounts:log_in')
@admin_only
def stores_to_review(request):
    """عرض صفحة تحتوي على جميع المتاجر التي تنتظر المراجعة"""
    stores = Store.objects.filter(status='pending').order_by('-updated_at')
    context = {
        'stores': stores,
    }
    return render(request, 'management/stores_to_review.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def products_to_review(request):
    """عرض صفحة تحتوي على جميع المنتجات التي تنتظر المراجعة"""
    products = Product.objects.filter(status='checking').order_by('-updated_at')
    context = {
        'products': products,
    }
    return render(request, 'management/products_to_review.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
def orders_to_review(request):
    """عرض صفحة تحتوي على جميع الطلبات التي تنتظر المراجعة"""
    orders = Order.objects.filter(verification_status='checking').order_by('-updated_at')
    context = {
        'orders': orders,
    }
    return render(request, 'management/orders_to_review.html', context)
