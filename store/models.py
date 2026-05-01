from django.db import models
from django_ckeditor_5.fields import CKEditor5Field   
from accounts.models import Store


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255 , verbose_name="اسم المنتج", help_text="قم بإدخال اسم المنتج")
    thumbnail_img = models.ImageField(upload_to='vendors/Products/thumbnails' , verbose_name="صورة المنتج الرئيسية", help_text="قم بإدخال صورة المنتج الرئيسية التي ستظهر في صفحة المتجر وصفحة تفاصيل المنتج")
    description = CKEditor5Field('الوصف', config_name='default', help_text="قم بإدخال وصف وتفاصيل المنتج ")
    upload_at = models.DateTimeField(auto_now_add=True , verbose_name='تاريخ الإنشاء')
    show = models.BooleanField(default=False , verbose_name='عرض للزبائن', help_text="قم بالأختيار ان كنت ترغب بعرض المنتج للزبائن مباشرة \n ان لم تقم بتحديده سيتم إخفاء المنتج ولن يتمكن زبائنك من رؤيته")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2 , verbose_name="سعر الشراء", help_text="أدخل سعر الجملة الذي اشتريت به المنتج")
    price = models.DecimalField(max_digits=10, decimal_places=2 , verbose_name="سعر البيع", help_text="أدخل سعر البيع النهائي للمنتج ")
    offer = models.BooleanField(default=False , verbose_name="تخفيض", help_text="قم بتحديد هذا الخيار في حال كان المنتج عليه عرض تخفيض")
    offer_price = models.DecimalField(default=0 , max_digits=10, decimal_places=2 , verbose_name="السعر بعد التخفيض", help_text="أدخل سعر التخفيض الخاص بالمنتج")
    free_delivery = models.BooleanField(default=False , verbose_name="توصيل مجاني", help_text="قم بتحديد هذا الخيار في حال كنت تقدم خدمة التوصيل المجاني لهذا المنتج")
    total_sales = models.PositiveIntegerField(default=0 , verbose_name="عدد المبيعات", help_text="اجمالي عدد مرات بيع المنتج")
    status = models.CharField(verbose_name='حالة المنتج', max_length=20, choices=[('checking', 'جاري المراجعة'), ('approved', 'مقبول'), ('rejected', 'مرفوض')], default='checking')
    rejected_cause = models.TextField(verbose_name='سبب الرفض', blank=True, null=True, help_text='في حال تم رفض المنتج،سيتم عرض سبب الرفض هنا')
    has_sizes = models.BooleanField(default=True, verbose_name='المنتج له مقاسات', help_text='قم بالتحديد ان كان المنتج الخاص بك له عدة مقاسات')
    type = models.CharField(verbose_name='نوع المنتج', choices=[('clothes','ملابس'),('watches','ساعات'), ('Accessories','اكسسوارات')] , default='clothes', help_text="قم بإختيار نوع المنتج الخاص بك")
    gender = models.CharField( verbose_name="الجنس المستهدف", max_length=20, choices=[('male', 'رجالي'), ('female', 'نسائي'), ('unisex', 'كلا الجنسين')], default='unisex', help_text="حدد إن كان المنتج موجّه للرجال أو النساء أو مناسب لكلا الجنسين")
    max_quantity_per_order = models.PositiveIntegerField(default=10 , verbose_name="الكمية القصوى للطلب", help_text="حدد الحد الأقصى لعدد القطع التي يمكن للزبون طلبها من هذا المنتج في طلب واحد")

    class Meta:
        verbose_name = 'منتج'
        verbose_name_plural = 'المنتجات'

    def __str__(self):
        return self.name
    
    def get_price(self):
        """تعيد سعر المنتج وفقا لحالة التخفيض """
        if self.offer :
            return self.offer_price
        else:
            return self.price
        
class ProductImages(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE , verbose_name='المنتج')
    priority = models.PositiveIntegerField(default=1 , verbose_name='الأولوية', help_text='حدد الأولوية للصورة في عرض المنتج') # . يمكنك استخدام هذا الحقل لترتيب الصور حسب الأهمية. على سبيل المثال، يمكنك تعيين الأولوية 1 للصورة الرئيسية، والأولوية 2 للصورة الثانية، وهكذا.
    image = models.ImageField(upload_to='store/Products/images' , verbose_name='الصورة')
    def __str__(self):
        return self.product.name
    
    class Meta:
        verbose_name = 'صورة المنتج'
        verbose_name_plural = 'صور المنتج'
        
class ProductColor(models.Model):
    product = models.ForeignKey(Product, related_name='colors', on_delete=models.CASCADE , verbose_name='المنتج')
    color = models.CharField(max_length=50 , verbose_name='اللون')
    image = models.ImageField(upload_to='store/Products/colors/', null=True , verbose_name='الصورة' , help_text='يمكنك إضافة صورة للون المنتج لتسهيل تمييزه من قبل الزبائن')
    available = models.BooleanField(default=True , verbose_name='متوفر', help_text='قم بتحديد هذا الخيار في حال كان هذا اللون متوفر حاليا في المخزون \n ان لم تقم بتحديده سيتم إخفاء هذا اللون ولن يتمكن زبائنك من رؤيته \n في حال عدم توفر هذا اللون سيتم ايضا اخفاء جميع المقاسات المرتبطة به')
    
    def __str__(self):
        return f"{self.product.name} - {self.color}"
    
    def save(self, *args, **kwargs):
        """تقوم هذه الدالة بحفظ لون المنتج وفي حال تم تحديده كغير متوفر يتم ايضا جعل جميع المقاسات المرتبطة به غير متوفرة"""
        super().save(*args, **kwargs)
        if not self.available:
            # اجعل كل المقاسات التابعة لهذا اللون غير متوفرة
            self.sizes.update(available=False)
    
    class Meta:
        verbose_name = 'لون المنتج'
        verbose_name_plural = 'ألوان المنتج'

class ProductSize(models.Model):
    # يتم انشاء هذا النموذج فقط في حال كان المنتج له مقاسات متعددة 
    product_color = models.ForeignKey(ProductColor, related_name='sizes', on_delete=models.CASCADE , verbose_name='المنتج')
    size = models.CharField(max_length=10 , verbose_name='المقاس' , help_text='قم بإدخال المقاس الخاص بالمنتج مثل S أو M أو L أو 40 أو 41 أو أي مقاس آخر يتناسب مع نوع المنتج')
    available = models.BooleanField(default=True , verbose_name='متوفر', help_text='قم بتحديد هذا الخيار في حال كان هذا المقاس متوفر حاليا في المخزون \n ان لم تقم بتحديده سيتم إخفاء هذا المقاس ولن يتمكن زبائنك من رؤيته ')

    def __str__(self):
        return f"{self.product_color.color} - {self.size}"
    
    def save(self, *args, **kwargs):
        """تقوم هذه الدالة بحفظ مقاس المنتج وفي حال تم تحديده كمتوفر يتم ايضا جعل لون المنتج المرتبط به متوفر"""
        super().save(*args, **kwargs)
        if self.available:
            # اجعل اللون الأب متوفر إذا كان هذا المقاس متوفر
            self.product_color.available = True
            self.product_color.save(update_fields=['available'])

    
    class Meta:
        verbose_name = 'مقاس المنتج'
        verbose_name_plural = 'مقاسات المنتج'

class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders', verbose_name='المتجر')
    
    # حقول بيانات الطلب
    serial_number = models.PositiveIntegerField(default=1, verbose_name='الرقم التسلسلي') 
    verification_status = models.CharField(verbose_name='حالة التحقق', max_length=20, choices=[('checking','جاري التحقق'), ('approved','طلب حقيقي'), ('rejected','طلب وهمي'),], default='checking')
    status = models.CharField(verbose_name='حالة الطلب', max_length=20, choices=[('processing', 'جاري التجهيز'), ('delivered', 'تم التسليم'), ('canceled', 'ملغي')], default='processing')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الطلب')
    
    # حقول المنتج المطلوب
    product = models.ForeignKey(Product, on_delete=models.SET_NULL , verbose_name='المنتج', null=True) # عند حذف المنتج كي لا تحصل مشاكل بالطلب تم اضافة null=True
    product_name = models.CharField(max_length=100,  verbose_name='اسم المنتج' )
    product_color = models.CharField(max_length=100,  verbose_name='لون المنتج' )
    product_size = models.CharField(max_length=100,  verbose_name='مقاس المنتج', null=True)
    product_qty = models.PositiveIntegerField(verbose_name='الكمية المطلوبة')
    purchase_price = models.PositiveIntegerField() # يتم تحديد هذا الخيار تلقائيا عند انشاء طلب وفقا لحاله قرينه في المنتج المطلوب
    selling_price = models.PositiveIntegerField() # يتم تحديد هذا الخيار تلقائيا عند انشاء طلب وفقا لحاله قرينه في المنتج المطلوب
    free_delivery = models.BooleanField(default=False , verbose_name="توصيل مجاني", )    # يتم تحديد هذا الخيار تلقائيا عند انشاء طلب وفقا لحاله قرينه في المنتج المطلوب
    
    # حقول بيانات الزبون 
    customer_name = models.CharField(max_length=100, verbose_name='اسم الزبون')
    customer_phone = models.CharField(max_length=100, verbose_name='رقم هاتف الزبون')
    customer_location = models.CharField(max_length=100, verbose_name='عنوان الزبون')
    note =  CKEditor5Field('ملاحظة', config_name='default',)
    
    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        
    def __str__(self):
        return self.store.name + " - " + str(self.serial_number)
    
    def create_serial_number(self):
        """تقوم هذه الدالة بإنشاء رقم تسلسلي فريد لكل طلب يتم انشاءه في المتجر بناءا على عدد الطلبات السابقة للمتجر"""
        last_order = Order.objects.filter(store=self.store).order_by('serial_number').last()
        if last_order:
            return last_order.serial_number + 1
        else:
            return 1
    
#change-later ضيف اوردر ايتم مشان اذا ضفت تحديث سلة وامكانية طلب اكثر من منتج سوا بعدين ماتتعب