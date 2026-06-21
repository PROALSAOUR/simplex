from django.db import models
from accounts.models import Store
from Project.settings import COMMISSION_RATE
from decimal import Decimal

class Recipe(models.Model):
    invoice_number = models.CharField(max_length=30, unique=True, verbose_name='رقم الفاتورة', null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='recipes', verbose_name='المتجر')
    
    # معلومات الفترة
    billing_year = models.PositiveIntegerField(verbose_name='السنة')
    billing_month = models.PositiveIntegerField(verbose_name='الشهر')
    
    # بيانات الحساب
    total_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='إجمالي المبيعات'
    )
    
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=COMMISSION_RATE,
        verbose_name='نسبة العمولة'
    )

    commission_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='قيمة العمولة'
    )
    
    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='الخصم'
    )
    
    STATUS_CHOICES = [
        ('pending', 'بانتظار الدفع'),
        ('paid', 'مدفوعة'),
        ('cancelled', 'ملغاة'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    paid_at = models.DateTimeField( null=True, blank=True, verbose_name='تاريخ الدفع')
    notes = models.TextField( blank=True, verbose_name='ملاحظات')

    created_at = models.DateTimeField( auto_now_add=True , verbose_name='تاريخ الإنشاء')

    def __str__(self):
        return f"{self.invoice_number} - {self.store.name}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'store',
                    'billing_year',
                    'billing_month'
                ],
                name='unique_monthly_invoice'
            )
        ]
    
    @property
    def final_value(self):
        """يحسب القيمة النهائية للفاتورة بعد خصم الخصم."""
        return self.commission_value - self.discount
    
    @staticmethod
    def generate_invoice_number(invoice):
        """
        توليد رقم فاتورة فريد اعتماداً على:
        - سنة الفوترة (billing_year)
        - شهر الفوترة (billing_month)
        - معرف الفاتورة (ID)

        صيغة الرقم:
        INV-YYYY-MM-XXXXXX

        مثال:
        INV-2026-06-000125

        يعتمد الرقم على معرف الفاتورة الفريد في قاعدة البيانات，
        مما يضمن عدم تكرار أرقام الفواتير حتى عند إنشاء عدة
        فواتير بشكل متزامن بواسطة Celery أو من عدة عمليات
        مختلفة.

        يجب استدعاء هذه الدالة بعد حفظ الفاتورة لأول مرة
        حتى يكون حقل ID متوفراً.
        """
        return (
            f"INV-{invoice.billing_year}-"
            f"{invoice.billing_month:02d}-"
            f"{invoice.id:06d}"
        )
        
def calculate_commission(total_sales):
    """
    حساب العمولة التقديرية المستحقة على المتجر
    خلال الشهر الحالي بناءً على إجمالي المبيعات
    ونسبة العمولة المحددة في إعدادات النظام.
    """
    return total_sales * Decimal(str(COMMISSION_RATE)) / Decimal("100")