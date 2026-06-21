from celery import shared_task
from accounts.models import Store
from datetime import timedelta
from django.utils import timezone
from management.models import Recipe, calculate_commission
from django.db import transaction 
from django.db.models import Sum
from Project.settings import COMMISSION_RATE


@shared_task
def create_monthly_invoices():
    """
    إنشاء الفواتير الشهرية للمتاجر.

    تقوم هذه المهمة المجدولة بالعمل في اليوم الأول من كل شهر، وتمر
    على جميع المتاجر التي مضى على إنشائها 30 يوماً أو أكثر، ثم تنشئ
    فاتورة شهرية للمتاجر المستحقة وفق الخطوات التالية:

    1. جلب جميع المتاجر المؤهلة للفوترة.
    2. التحقق من عدم وجود فاتورة للمتجر لنفس الشهر والسنة.
    3. جلب جميع الطلبات التي:
    - تم تسليمها.
    - تم التحقق من صحتها.
    - لم يتم ربطها بفاتورة سابقة.
    - تاريخ تسليمها ضمن الشهر الحالي.
    4. حساب إجمالي المبيعات للطلبات المؤهلة.
    5. في حال كان إجمالي المبيعات صفراً، يتم تجاهل المتجر وعدم إنشاء فاتورة.
    6. حساب قيمة العمولة اعتماداً على إجمالي المبيعات ونسبة العمولة
    المعتمدة في النظام.
    7. إنشاء الفاتورة وتخزين جميع القيم المحاسبية (إجمالي المبيعات،
    نسبة العمولة، وقيمة العمولة) لضمان ثبات البيانات وعدم تأثرها
    بأي تعديلات مستقبلية على الطلبات أو إعدادات النظام.
    8. ربط جميع الطلبات المستخدمة في الحساب بالفاتورة التي تم إنشاؤها
    لمنع احتسابها مرة أخرى في أي فاتورة مستقبلية.

    مميزات هذه الآلية:
    - تمنع إنشاء أكثر من فاتورة للمتجر خلال نفس الشهر.
    - تمنع احتساب الطلب الواحد أكثر من مرة.
    - تحفظ القيم المحاسبية كما كانت وقت إصدار الفاتورة.
    - تضمن أن أول فاتورة للمتجر لا تُنشأ إلا بعد مرور 30 يوماً
    على تاريخ إنشاء المتجر.
    - تعمل داخل معاملة (Transaction) لكل متجر لضمان سلامة البيانات
    في حال حدوث أي خطأ أثناء إنشاء الفاتورة.
    """
    
    stores = Store.objects.filter(
        created_at__lte=timezone.now() - timedelta(days=30) # اجلب جميع المتاجر التي مضى على إنشائها 30 يوماً أو أكثر.
    )
    year = timezone.now().year
    month = timezone.now().month
    
    for store in stores :
        try:
            with transaction.atomic():
                # تحقق إذا كانت الفاتورة لهذا الشهر موجودة أصلاً
                if Recipe.objects.filter(
                    store=store,
                    billing_year=year,
                    billing_month=month
                ).exists():
                    continue
                
                # جلب الطلبات المسلمة هذا الشهر
                orders = store.orders.filter(
                    invoice__isnull=True,
                    status='delivered',
                    verification_status='approved',
                    delivery_date__year=year,
                    delivery_date__month=month
                )
                
                # حساب المبيعات
                total_sales = ( orders.aggregate( total=Sum('total_selling_price'))['total'] or 0 )
                if total_sales <= 0: # متجر لم يبيع هذا الشهر لاتنشئ له فاتورة
                    continue
                # حساب العمولة
                commission_value = calculate_commission(total_sales)
                # إنشاء الفاتورة
                invoice = Recipe.objects.create(
                    store = store,
                    billing_year=year,
                    billing_month=month,
                    total_sales=total_sales,
                    commission_rate= COMMISSION_RATE,
                    commission_value = commission_value,
                )
                # ربط الفاتورة بالطلبات
                orders.update(invoice=invoice)
                # ارسال تنبيه للبائع
        except Exception:
            #change-later ضيف لوجر لتسجيل الاخطاء
            # logger.exception(
            #     f"Failed to create invoice for store {store.id}"
            # )
            pass