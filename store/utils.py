# ===========================
# دوال بطاقات الاحصائيات بلوحة التحكم

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
