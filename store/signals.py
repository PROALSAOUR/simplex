from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from store.models import *

# تم تسليم المنتج =  تاريخ التسليم وزيادة كمية المبيعات المنتج
# تم الغاء المنتج بعد التسليم = تقليل كمية المبيعات المنتج

@receiver(pre_save, sender=Product)
def handle_product_status_change(sender, instance, **kwargs):
    """
    عند تغيير حالة المنتج إلى تم القبول:
    يتم حذف سبب الرفض في حال وجوده، لأنه لا معنى لوجود سبب رفض لمنتج تم قبوله.
    """
    
    # الطلب جديد وليس تعديل
    if not instance.pk:
        return
    
    try:
        old_product = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        return
    
        # عند التحويل إلى تم القبول
    if old_product.status != 'approved' and instance.status == 'approved':

        # حذف سبب الرفض في حال وجوده
        instance.rejected_cause = ''

                