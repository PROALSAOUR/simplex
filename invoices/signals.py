from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from invoices.models import Invoice

@receiver(post_save, sender=Invoice)
def generate_invoice_number_signal(sender, instance, created, **kwargs):
    """
    إنشاء رقم الفاتورة تلقائياً بعد إنشاء السجل لأول مرة.
    """
    if created and not instance.invoice_number:
        instance.invoice_number = Invoice.generate_invoice_number(instance)

        Invoice.objects.filter(
            pk=instance.pk
        ).update(
            invoice_number=instance.invoice_number
        )
        
@receiver(post_save, sender=Invoice)
def handle_recipe_paid_date(sender, instance, **kwargs):
    """
    عند تغيير حالة الفاتورة إلى تم الدفع:
    - إضافة تاريخ الدفع
    
    """
    
    # الفاتورة جديدة وليس تعديل
    if not instance.pk:
        return
    
    try:
        old_invoice = Invoice.objects.get(pk=instance.pk)
    except Invoice.DoesNotExist:
        return
    
    # =========================================
    # عند تحويل الحالة  إلى تم الدفع
    if old_invoice.status != 'paid' and instance.status == 'paid':
        # إضافة تاريخ الدفع
        instance.paid_at = timezone.now()
                
    # =========================================
   