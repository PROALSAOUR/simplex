from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from store.models import Product
from accounts.models import Store
from management.models import Recipe

"""
يمكن تعديل الطلبات التي حالتها جاري التجهيز فقط ولايمكن تعديل الطلبات المستلمة او الملغية
لايمكن تعديل عناصر الطلب حاليا لذا في حال اراد المستخدم التعديل عليها عليه الغاء الطلب واعادة انشاءه
لايمكن حذف الطلبات 
يتم عرض جميع الطلبات للمستخدم الا الطلبات التي لم يتم التحقق من  وهميتها او صحتها بعد 
ان كان الطلب وهمي لايمكن تعديله
يمكن لكل من الادارة والبائعين تعديل الطلبات لكن الادارة لايمكنها اضافة طلبات يدويا
بمجرد ان تقوم الاداري بتحديد طلب على انه وهمي يتم تحويل حالته عن طريق الاشارات تلقائيا من جاري التجهيز الى ملغي و لايمكن تعديله بعد ذلك
"""

#change-later ضيف بالاحصائيات حساب لمتوسط مدة تسليم الطلب بين تاريخ الانشاء وتارخ التسليم 

class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders', verbose_name='المتجر')

    invoice = models.ForeignKey(
        Recipe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders'
    )

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
        help_text='حالة التحقق من الطلب: جاري التحقق: الطلب لم يتم التحقق منه بعد | طلب حقيقي: تم التحقق من صحة الطلب | طلب وهمي: تم رفض الطلب لعدم صحته',
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

    # حقول قيم الطلب
    total_purchase_price = models.PositiveIntegerField(verbose_name='إجمالي سعر الشراء', default=0, help_text='إجمالي تكلفة المنتجات في الطلب، محسوبة بناءً على أسعار الشراء لكل منتج والكمية المطلوبة.')
    total_selling_price = models.PositiveIntegerField(verbose_name='إجمالي سعر البيع', default=0, help_text='إجمالي سعر البيع للطلب، محسوبة بناءً على أسعار البيع لكل منتج والكمية المطلوبة.')
    total_profit = models.IntegerField(verbose_name='الربح', default=0, help_text='الربح المحقق من الطلب، محسوبًا كفرق بين إجمالي سعر البيع وإجمالي سعر الشراء.')

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

    def calculate_totals(self):
        """
        حساب إجمالي الأسعار والأرباح من عناصر الطلب.
        تحسب الإجماليات بناءً على:
        - إجمالي سعر الشراء = مجموع (سعر الشراء × الكمية) لكل عنصر
        - إجمالي سعر البيع = مجموع (سعر البيع × الكمية) لكل عنصر  
        - الربح الإجمالي = إجمالي سعر البيع - إجمالي سعر الشراء
        """
        from django.db.models import F, Sum
        
        totals = self.items.aggregate(
            total_purchase=Sum(F('purchase_price') * F('qty')),
            total_selling=Sum(F('selling_price') * F('qty')),
        )
        
        self.total_purchase_price = totals.get('total_purchase') or 0
        self.total_selling_price = totals.get('total_selling') or 0
        self.total_profit = self.total_selling_price - self.total_purchase_price

class OrderItem(models.Model):
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
