"""
شرح عمل إحصائيات لوحة تحكم المتجر

الفكرة العامة
-------------
لوحة التحكم تعرض 4 بطاقات: المبيعات، الطلبات، المنتجات، المشاهدات.
كل بطاقة (ما عدا المنتجات) تقارن الفترة الحالية بالفترة السابقة لها.
مثال: عند اختيار "هذا الشهر" تُقارَن الأيام الماضية من هذا الشهر بنفس
عدد الأيام من الشهر الماضي.

مسار التنفيذ
------------
store_dashboard (views.py)
    └─ get_dashboard_stats(store, date_range)        <- الدالة الرئيسية
          ├─ get_period_dates(...)                   <- تحديد الفترتين
          │     └─ shift_months(...)                 <- إزاحة التاريخ بالأشهر
          ├─ between(...)                            <- بناء شرط التاريخ
          ├─ calculate_change(...)                   <- نص ولون التغيير
          │     └─ format_number(...)                <- تنسيق الأرقام
          └─ ترجع قاموس stats جاهزًا للقالب و JSON

الثوابت
-------
PERIODS         : قيم الفلتر المسموحة. أي قيمة أخرى تُستبدل بـ DEFAULT_PERIOD.
DEFAULT_PERIOD  : الفترة الافتراضية ('this_month').

shift_months(dt, months)
-----------------------
تُزيح تاريخًا بعدد أشهر (موجب للمستقبل، سالب للماضي).
إذا كان اليوم غير موجود في الشهر الهدف تستخدم آخر يوم فيه
(مثال: 31 مارس بعد إزاحة -1 تصبح 28 فبراير).
السنة تُزاح بـ 12 شهرًا (months=-12).


get_period_dates(date_range, now)
---------------------------------
ترجع 4 قيم: (بداية الحالية، نهاية الحالية، بداية السابقة، نهاية السابقة).
- كل الحسابات بالتوقيت المحلي للمشروع (localtime) لتفادي فروق UTC.
- نهاية الفترة الحالية = "الآن"، ونهاية السابقة = "الآن" مُزاحًا للخلف.
  هذا يجعل المقارنة عادلة (نفس المدة الزمنية في الفترتين).
- الفترات:
    today      : من منتصف الليل حتى الآن، مقابل نفس الساعات من أمس.
    this_month : من أول الشهر حتى الآن، مقابل الشهر الماضي بنفس المدة.
    this_year  : من أول يناير حتى الآن، مقابل السنة الماضية بنفس المدة.
    all        : ترجع (None, None, None, None) أي بدون فترات.
- النهاية دائمًا مستبعدة في الاستعلام (< وليس <=).
- لإضافة فترة جديدة (مثل الأسبوع): أضف فرعًا هنا، وأضف اسمها إلى
  PERIODS، وأضف خيارًا في <select> بالقالب.


between(field, start, end)
--------------------------
تبني شرط Q لحقل تاريخ: start <= field < end.
إذا كان start فارغًا (حالة 'all') ترجع Q() فارغًا، أي بدون تقييد،
فيُحسب كل شيء. هذا يغنينا عن كتابة حالة خاصة لكل تجميع.


format_number(value)
--------------------
تنسق رقمًا بفواصل الآلاف وبحد أقصى خانتين عشريتين، وتحذف الأصفار
الزائدة (1250.50 -> '1,250.5' ، 3.00 -> '3').
تُستخدم حاليًا فقط داخل نص التغيير.


calculate_change(current_value, previous_value)
-----------------------------------------------
ترجع قاموسًا: {'percentage', 'class', 'text'}
- الاتجاه (زيادة/نقصان) يُحدَّد من الفرق الفعلي وليس من النسبة المقرّبة،
  حتى لا تظهر زيادة صغيرة على أنها نقصان.
- الحالات:
    1) القيمتان متساويتان         -> 'لا تغيير'، بدون كلاس.
    2) الفترة السابقة = 0         -> '+الفرق ▲' (لا يمكن حساب نسبة من صفر)،
                                     كلاس 'complete'.
    3) غير ذلك                    -> 'النسبة% ▲' أو '▼' بخانة عشرية واحدة،
                                     كلاس 'complete' للزيادة و 'cancel' للنقصان.
- الكلاسات 'complete' و 'cancel' هي التي يلوّنها CSS (أخضر / أحمر).
- 'percentage' رقم للاستخدام البرمجي فقط (سالب عند النقصان)،
  والقالب يعرض 'text' فقط.


get_dashboard_stats(store, date_range)
--------------------------------------
الدالة الرئيسية. تنفذ 3 استعلامات فقط:
  1) تجميع الطلبات: المبيعات وعدد الطلبات للفترتين معًا.
  2) تجميع المشاهدات للفترتين معًا.
  3) عدد المنتجات الحالي (لا يعتمد على الفترة).

آلية التجميع الشرطي:
  بدل استعلام لكل فترة، نستخدم Sum/Count مع filter=...، فيحسب قاعدة
  البيانات القيمتين في مرور واحد على الجدول. تُبنى أسماء التجميعات
  آليًا في حلقة: current_sales, previous_sales, current_orders ...

ملاحظات مهمة:
  - المبيعات: تحسب الطلبات status='delivered' حسب delivery_date.
  - الطلبات: تحسب كل الحالات حسب order_date (تشمل الملغاة حاليًا).
    لاستبعاد الملغاة أضف ~Q(status='cancelled') في فلتر Count.
  - المشاهدات: تُقيَّد بـ viewed_at >= بداية الفترة السابقة لتقليل المسح
    (لا حاجة لقراءة ما هو أقدم منها). في حالة 'all' لا يوجد تقييد.
  - في حالة 'all' لا تُبنى تجميعات previous_* أصلًا، ولذلك نستخدم
    .get('previous_...') التي ترجع None بدل KeyError، وتُعرض النصوص
    'منذ الافتتاح' بدل نص مقارنة.
  - المبيعات تُقرَّب لعدد صحيح لتطابق floatformat:0 في القالب.

البنية المُرجَعة (يعتمد عليها القالب و JavaScript، لا تغيّر أسماءها):
  {
    'sales':    {'value': رقم, 'change': {'percentage', 'class', 'text'}},
    'orders':   {...},
    'products': {...},   # التغيير فيها نص ثابت بدون مقارنة
    'views':    {...},
  }

لإضافة بطاقة جديدة:
  1) أضف تجميعها في الحلقة (order_aggs أو view_aggs أو استعلام جديد).
  2) أضف مفتاحها في القاموس المُرجَع بنفس البنية.
  3) أضف البطاقة في القالب، وأضف مفتاحها في مصفوفة JavaScript
     ['sales', 'orders', 'products', 'views'] وعناصر الـ id الخاصة بها.


=====================================================================
"""

import calendar
from datetime import timedelta
from django.db.models import Count, Q, Sum
from django.utils import timezone
from orders.models import Order
from store.models import Product, ProductView


PERIODS = ('today', 'this_month', 'this_year', 'all')
DEFAULT_PERIOD = 'this_month'


def shift_months(dt, months):
    """يزيح التاريخ بعدد أشهر مع مراعاة اختلاف أيام الشهور (31 مارس -> 28 فبراير)."""
    year, month = divmod(dt.year * 12 + dt.month - 1 + months, 12)
    month += 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def get_period_dates(date_range, now):
    """
    يرجع (بداية الحالية، نهاية الحالية، بداية السابقة، نهاية السابقة).
    الفترة السابقة تنتهي في نفس اللحظة النسبية لضمان مقارنة عادلة.
    """
    now = timezone.localtime(now)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if date_range == 'today':
        start = midnight
        return start, now, start - timedelta(days=1), now - timedelta(days=1)

    if date_range == 'this_month':
        start = midnight.replace(day=1)
        return start, now, shift_months(start, -1), shift_months(now, -1)

    if date_range == 'this_year':
        start = midnight.replace(month=1, day=1)
        return start, now, shift_months(start, -12), shift_months(now, -12)

    return None, None, None, None


def between(field, start, end):
    """شرط تاريخ [start, end). بدون تواريخ = كل الفترات."""
    if start is None:
        return Q()
    return Q(**{f'{field}__gte': start, f'{field}__lt': end})


def format_number(value):
    return f'{value:,.2f}'.rstrip('0').rstrip('.')

def calculate_change(current_value, previous_value):
    """حساب التغيير وإرجاع نص مختصر يناسب بطاقة الإحصائيات."""
    current_value = float(current_value or 0)
    previous_value = float(previous_value or 0)
    difference = current_value - previous_value

    if difference == 0:
        return {'percentage': 0, 'class': '', 'text': 'لا تغيير'}

    is_increase = difference > 0
    css_class = 'complete' if is_increase else 'cancel'
    arrow = '▲' if is_increase else '▼'

    # لا يمكن حساب نسبة من صفر، فنعرض مقدار الزيادة الفعلي.
    # (النقصان من صفر مستحيل لأن القيم لا تكون سالبة)
    if previous_value == 0:
        return {
            'percentage': None,
            'class': css_class,
            'text': f'+{format_number(difference)} {arrow}',
        }

    percentage = round(abs(difference) / previous_value * 100, 1)

    return {
        'percentage': percentage if is_increase else -percentage,
        'class': css_class,
        'text': f'{percentage:g}% {arrow}',
}
    
def get_dashboard_stats(store, date_range):
    """يحسب إحصائيات المتجر في 3 استعلامات فقط."""
    now = timezone.now()
    current_start, current_end, previous_start, previous_end = (
        get_period_dates(date_range, now)
    )
    has_comparison = date_range != 'all'

    # بناء التجميعات لكل فترة بدل تكرار الشروط يدويًا.
    periods = {'current': (current_start, current_end)}
    if has_comparison:
        periods['previous'] = (previous_start, previous_end)

    order_aggs, view_aggs = {}, {}
    for name, (start, end) in periods.items():
        order_aggs[f'{name}_sales'] = Sum(
            'total_selling_price',
            filter=Q(status='delivered') & between('delivery_date', start, end),
        )
        order_aggs[f'{name}_orders'] = Count(
            'id', filter=between('order_date', start, end)
        )
        view_aggs[f'{name}_views'] = Count(
            'id', filter=between('viewed_at', start, end)
        )

    order_stats = Order.objects.filter(store=store).aggregate(**order_aggs)

    product_views = ProductView.objects.filter(product__store=store)
    if has_comparison:
        # لا حاجة لقراءة مشاهدات أقدم من بداية الفترة السابقة.
        product_views = product_views.filter(viewed_at__gte=previous_start)
    views_stats = product_views.aggregate(**view_aggs)

    products_count = Product.objects.filter(store=store).count()

    def build_change(current, previous):
        if not has_comparison:
            return {'percentage': None, 'class': '', 'text': 'منذ الافتتاح'}
        return calculate_change(current, previous)

    sales = order_stats['current_sales'] or 0
    orders_count = order_stats['current_orders'] or 0
    views_count = views_stats['current_views'] or 0

    return {
        'sales': {
            'value': round(float(sales)),
            'change': build_change(sales, order_stats.get('previous_sales')),
        },
        'orders': {
            'value': orders_count,
            'change': build_change(orders_count, order_stats.get('previous_orders')),
        },
        'products': {
            'value': products_count,
            'change': {
                'percentage': None,
                'class': '',
                'text': 'إجمالي المنتجات',
            },
        },
        'views': {
            'value': views_count,
            'change': build_change(views_count, views_stats.get('previous_views')),
        },
    }
