from django.http import Http404, JsonResponse
from django.shortcuts import  render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from accounts.models import Store
from accounts.validators import get_user_type 
from accounts.decorators import admin_only 
from invoices.models import calculate_commission, Invoice

from invoices.forms import *

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
    return render(request, 'admins/store_statistics.html', context)
