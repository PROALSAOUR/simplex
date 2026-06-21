from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from management.models import Recipe

@receiver(post_save, sender=Recipe)
def generate_invoice_number_signal(sender, instance, created, **kwargs):
    """
    إنشاء رقم الفاتورة تلقائياً بعد إنشاء السجل لأول مرة.
    """
    if created and not instance.invoice_number:
        instance.invoice_number = Recipe.generate_invoice_number(instance)

        Recipe.objects.filter(
            pk=instance.pk
        ).update(
            invoice_number=instance.invoice_number
        )
        
@receiver(post_save, sender=Recipe)
def handle_recipe_paid_date(sender, instance, **kwargs):
    """
    عند تغيير حالة الفاتورة إلى تم الدفع:
    - إضافة تاريخ الدفع
    
    """
    
    # الفاتورة جديدة وليس تعديل
    if not instance.pk:
        return
    
    try:
        old_invoice = Recipe.objects.get(pk=instance.pk)
    except Recipe.DoesNotExist:
        return
    
    # =========================================
    # عند تحويل الحالة  إلى تم الدفع
    if old_invoice.status != 'paid' and instance.status == 'paid':
        # إضافة تاريخ الدفع
        instance.paid_at = timezone.now()
                
    # =========================================
   