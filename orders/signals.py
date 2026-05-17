from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from orders.models import *

# تم تسليم المنتج =  تاريخ التسليم وزيادة كمية المبيعات المنتج
# تم الغاء المنتج بعد التسليم = تقليل كمية المبيعات المنتج

@receiver(pre_save, sender=Order)
def handle_order_delivery(sender, instance, **kwargs):
    """
    عند تغيير حالة الطلب إلى تم التسليم:
    - إضافة تاريخ التسليم
    - زيادة عدد مبيعات المنتجات
    
    عند التحويل من تم التسليم الى ملغي بعد التسليم:
    - تقليل عدد مبيعات المنتجات
    """
    
    # الطلب جديد وليس تعديل
    if not instance.pk:
        return
    
    try:
        old_order = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return
    
    # =========================================
    # عند التحويل إلى تم التسليم
    if old_order.status != 'delivered' and instance.status == 'delivered':

        # إضافة تاريخ التسليم
        instance.delivery_date = timezone.now()

        # زيادة عدد المبيعات للمنتجات
        for item in instance.items.select_related('product'):
            if item.product:
                item.product.total_sales += item.qty
                item.product.save(update_fields=['total_sales'])
                
    # =========================================
    # عند إلغاء طلب تم تسليمه مسبقاً
    elif old_order.status == 'delivered' and instance.status == 'canceled':

        for item in instance.items.select_related('product'):
            if item.product:

                # منع النزول تحت الصفر
                item.product.total_sales = max(
                    0,
                    item.product.total_sales - item.qty
                )

                item.product.save(update_fields=['total_sales'])
                
                