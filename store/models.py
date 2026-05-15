from django.db import models
from django_ckeditor_5.fields import CKEditor5Field   
from accounts.models import Store


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255 , verbose_name="اسم المنتج", help_text="قم بإدخال اسم المنتج")
    thumbnail_img = models.ImageField(upload_to='store/Products/thumbnails' , verbose_name="صورة المنتج الرئيسية", help_text="قم بإدخال صورة المنتج الرئيسية التي ستظهر في صفحة المتجر وصفحة تفاصيل المنتج")
    description = CKEditor5Field('الوصف', config_name='default', help_text="قم بإدخال وصف وتفاصيل المنتج ")
    upload_at = models.DateTimeField(auto_now_add=True , verbose_name='تاريخ الإنشاء')
    is_visible = models.BooleanField(default=False , choices=[(True, "ظاهر"),(False, "مخفي"),], verbose_name='الظهور للزبائن', help_text="قم بالأختيار ان كنت ترغب بإظهار المنتج للزبائن مباشرة \n ان لم تقم بتحديده سيتم إخفاء المنتج ولن يتمكن زبائنك من رؤيته")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2 , verbose_name="سعر الشراء", help_text="أدخل سعر الجملة الذي اشتريت به المنتج")
    price = models.DecimalField(max_digits=10, decimal_places=2 , verbose_name="سعر البيع", help_text="أدخل سعر البيع النهائي للمنتج ")
    offer = models.BooleanField(default=False , verbose_name="تخفيض", help_text="قم بتحديد هذا الخيار في حال كان المنتج عليه عرض تخفيض")
    offer_price = models.DecimalField(default=0 , max_digits=10, decimal_places=2 , verbose_name="السعر بعد التخفيض", help_text="أدخل سعر التخفيض الخاص بالمنتج")
    free_delivery = models.BooleanField(default=False , verbose_name="توصيل مجاني", help_text="قم بتحديد هذا الخيار في حال كنت تقدم خدمة التوصيل المجاني لهذا المنتج")
    total_sales = models.PositiveIntegerField(default=0 , verbose_name="عدد المبيعات", help_text="اجمالي عدد مرات بيع المنتج")
    status = models.CharField(verbose_name='حالة المنتج', max_length=20, choices=[('checking', 'جاري المراجعة'), ('approved', 'مقبول'), ('rejected', 'مرفوض')], default='checking')
    rejected_cause = models.TextField(verbose_name='سبب الرفض', blank=True, null=True, help_text='في حال تم رفض المنتج،سيتم عرض سبب الرفض هنا')
    type = models.CharField(verbose_name='نوع المنتج', choices=[('clothes','ملابس'),('watches','ساعات'), ('Accessories','اكسسوارات')] , default='clothes', help_text="قم بإختيار نوع المنتج الخاص بك")
    gender = models.CharField( verbose_name="الجنس المستهدف", max_length=20, choices=[('male', 'رجالي'), ('female', 'نسائي'), ('unisex', 'كلا الجنسين')], default='unisex', help_text="حدد إن كان المنتج موجّه للرجال أو النساء أو مناسب لكلا الجنسين")
    max_quantity_per_order = models.PositiveIntegerField(default=10 , blank=True, verbose_name="الكمية القصوى للطلب", help_text="حدد الحد الأقصى لعدد القطع التي يمكن للزبون طلبها من هذا المنتج في طلب واحد")

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
    
    class Meta:
        verbose_name = 'لون المنتج'
        verbose_name_plural = 'ألوان المنتج'

class ProductSize(models.Model):
    # يتم انشاء هذا النموذج فقط في حال كان المنتج له مقاسات متعددة 
    product_color = models.ForeignKey(ProductColor, related_name='sizes', on_delete=models.CASCADE , verbose_name='المنتج')
    size = models.CharField(max_length=10 , verbose_name='المقاس' , help_text='قم بإدخال المقاس الخاص بالمنتج مثل S أو M أو L أو 40 أو 41 أو أي مقاس آخر يتناسب مع نوع المنتج')

    def __str__(self):
        return f"{self.product_color.color} - {self.size}"
    
    class Meta:
        verbose_name = 'مقاس المنتج'
        verbose_name_plural = 'مقاسات المنتج'
