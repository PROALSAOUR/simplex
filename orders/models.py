from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from store.models import Store, Product
"""
يمكن تعديل الطلبات التي حالتها جاري التجهيز فقط ولايمكن تعديل الطلبات المستلمة او الملغية
لايمكن تعديل عناصر الطلب حاليا لذا في حال اراد المستخدم التعديل عليها عليه الغاء الطلب واعادة انشاءه
لايمكن حذف الطلبات 
يتم عرض جميع الطلبات للمستخدم الا الطلبات التي لم يتم التحقق من  وهميتها او صحتها بعد 
ان كان الطلب وهمي لايمكن تعديله
يمكن لكل من الادارة والبائعين تعديل الطلبات لكن الادارة لايمكنها اضافة طلبات يدويا
"""

#change-later ضيف هيلب تيكست لكل الحقول
#change-later ضيف بالاحصائيات حساب لمتوسط مدة تسليم الطلب بين تاريخ الانشاء وتارخ التسليم 


class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders', verbose_name='المتجر')

    # حقول بيانات الطلب
    serial_number = models.PositiveIntegerField(default=1, verbose_name='الرقم التسلسلي')
    verification_status = models.CharField(
        verbose_name='حالة التحقق',
        max_length=20,
        choices=[
            ('checking', 'جاري التحقق'),
            ('approved', 'طلب حقيقي'),
            ('rejected', 'طلب وهمي'),
        ],
        default='checking',
    )
    status = models.CharField(
        verbose_name='حالة الطلب',
        max_length=20,
        choices=[
            ('processing', 'جاري التجهيز'),
            ('delivered', 'تم التسليم'),
            ('canceled', 'ملغي'),
        ],
        default='processing',
        help_text='حالة الطلب: جاري التجهيز:الطلب قيد المراجعة و التجهيز | تم التسليم: تم تسليم الطلب للزبون | ملغي: تم إلغاء الطلب من قبل الزبون أو المتجر',
    )
    free_delivery = models.BooleanField(default=False, verbose_name="قيمة التوصيل" , choices=[(True, "مجاني"), (False, "غير مجاني")], help_text="حدد ما إذا كان هذا الطلب مشمولًا بالتوصيل المجاني أم لا.")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الطلب')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ آخر تحديث')
    delivery_date = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ التسليم')

    # حقول بيانات الزبون
    customer_name = models.CharField(max_length=100, verbose_name='اسم الزبون', help_text='أدخل الاسم الكامل للزبون، مثل: محمد أحمد.')
    customer_phone = models.CharField(max_length=100, verbose_name='رقم هاتف الزبون', help_text='أدخل رقم هاتف الزبون، مثل: 0912345678.')
    customer_location = models.CharField(max_length=100, verbose_name='عنوان الزبون', help_text='أدخل عنوان التوصيل ، مثل: بنغازي - السلماني .')
    note = CKEditor5Field('ملاحظة', config_name='default', null=True, blank=True, help_text='يمكنك إضافة ملاحظات خاصة بالطلب، مثل تعليمات التوصيل أو طلبات خاصة من الزبون.')

    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'

    def __str__(self):
        return self.store.name + " - " + str(self.serial_number)

    def create_serial_number(self):
        """إنشاء رقم تسلسلي فريد لكل طلب داخل المتجر."""
        last_order = Order.objects.filter(store=self.store).order_by('serial_number').last()
        if last_order:
            return last_order.serial_number + 1
        return 1

class OredrItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='الطلب')
    # حقول المنتج المطلوب
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name='المنتج', null=True)
    image = models.ImageField(upload_to='orders/OrderItems/', verbose_name="صورة المنتج ")
    color = models.CharField(max_length=100, verbose_name='لون المنتج')
    size = models.CharField(max_length=100, verbose_name='مقاس المنتج', null=True)
    qty = models.PositiveIntegerField(verbose_name='الكمية المطلوبة')
    purchase_price = models.PositiveIntegerField(verbose_name='سعر الشراء')
    selling_price = models.PositiveIntegerField(verbose_name='سعر البيع')

    class Meta:
        verbose_name = 'منتج للطلب'
        verbose_name_plural = 'منتجات للطلب'

    def __str__(self):
        return self.product.name if self.product else "منتج محذوف"
