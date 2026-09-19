from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models as db_models
from django.db.models import Q, Sum ,F, ExpressionWrapper, DecimalField
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from accounts.models import Store
from accounts.validators import get_user_type 
from accounts.decorators import admin_only 
from invoices.models import calculate_commission, Invoice
from django.contrib import messages
from invoices.forms import *

@admin_only
@login_required(login_url='accounts:log_in')
def all_stores_invoices(request):
    """
    عرض جميع الفواتير الخاصة بجميع المتاجر
    وهي صفحة خاصة بالإدارة فقط    
    """
    
    invoices = Invoice.objects.all()
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
def store_invoices(request, sid):
    """
    عرض جميع الفواتير الخاصة بالمتجر
    بالإضافة الى عرض المبلغ المستحق هذا الشهر حتى الأن
    
    """
    store = get_object_or_404(Store, id=sid)
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
    return render(request, 'invoices/store_invoices.html', context)

@login_required(login_url='accounts:log_in')
def view_invoice(request, rid):
    """الدالة المسؤولة عن صفحة عرض تفاصيل الفاتورة"""
    
    invoice = get_object_or_404(Invoice, id=rid)
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
    
    return render(request, 'invoices/view_invoice.html', context)

@login_required(login_url='accounts:log_in')
@admin_only
@require_POST
def edit_invoice(request, rid):
    # التحقق من النموذج وتعديل الفاتورة ثم إعادة النتيجة بصيغة JSON

    invoice = get_object_or_404(Invoice, id=rid)

    if "discount" in request.POST:

        form = InvoiceDiscountForm(
            request.POST,
            commission_value=invoice.commission_value,
        )

        if not form.is_valid():
            return JsonResponse({
                "success": False,
                "errors": {
                    "discount": form.errors["discount"][0]
                }
            }, status=400)

        if invoice.status != "pending":
            return JsonResponse({
                "success": False,
                "errors": {
                    "discount": (
                        "لا يمكن تعديل الخصم إلا عندما تكون حالة"
                        "الفاتورة بانتظار الدفع."
                    )
                }
            }, status=400)

        invoice.discount = form.cleaned_data["discount"]
        invoice.save()

    elif "status" in request.POST:

        form = InvoiceStatusForm(request.POST)

        if not form.is_valid():
            return JsonResponse({
                "success": False,
                "errors": {
                    "status": form.errors["status"][0]
                }
            }, status=400)

        invoice.status = form.cleaned_data["status"]
        invoice.save()

    else:
        return JsonResponse({
            "success": False,
            "message": "لم يتم تحديد البيانات المراد تعديلها."
        }, status=400)

    return JsonResponse({
        "success": True,
        "message": "تم التعديل بنجاح",
    })

@login_required(login_url='accounts:log_in')
def store_statistics(request, sid):
    """
    عرض صفحة الاحصائيات الخاصة بالمتجر    
    """
    store = get_object_or_404(Store, id=sid)
    user_type = get_user_type(request.user)    
    # تحقق ان كان المستخدم بائع ان المتجر الذي يريد عرض احصائياته هو متجره
    if user_type == 'vendor' and store.owner != request.user: # لو البائع يحاول الوصول لمتجر ليس له علاقة به
        raise Http404("المتجر غير موجود")
    
    context = {
        'store': store,
    }
    return render(request, 'management/store_statistics.html', context)
