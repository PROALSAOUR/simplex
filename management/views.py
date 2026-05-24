from django.shortcuts import render, get_object_or_404
from accounts.decorators import admin_only 
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from accounts.models import Store

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

