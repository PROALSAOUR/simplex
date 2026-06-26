from django.db import models
from django.contrib.auth.models import User

"""
======== بالنسبة للبائع ========
تسجيل الدخول يتم من خلال اليوزرنيم والباسورد الخاصين بالبائع حيث يتم جلب المتجر المرتبط بهم والدخول اليه
يمكن تسجيل الدخول فقط ان كانت حالة المتجر  (مفعل او غير مفعل ) ولا يمكن تسجيل الدخول اذا كانت حالة الحساب قيد المراجعة لأن هذا يعني ان الادارة لم تتحقق من بيانات الحساب بعد
انشاء حساب بنموذج واحد يوجد به حقول البائع والمتجر معا لتسهيل عملية التسجيل وربط البائع بالمتجر مباشرة عند انشاء الحساب
يمكن فقط للمالك وهو ذو اقصى صلاحية اضافة او ازالة بائعين اخرين للمتجر وتحديد صلاحياتهم
يمكن للبائع اضافة وتعديل جميع بيانات المتجر بإستثناء الحالة والتيليجرام ورقم الهاتف حيث انه ان اراد تغيررهم عليه التواصل مع الادارة لكي يغيروها له
======== اما بالنسبة للإدارة ========
تسجيل الدخول يتم من خلال اليوزرنيم والباسورد الخاصين بالإدارة حيث يتم تسجيل الدخول من نفس الصفحة التي يسجل بها الباعة دخولهم ولكن يتم تمييزهم من خلال نوع المستخدم في ملف البروفايل الخاص بهم
يمكن للاداري ذو صلاحية السوبريوزر  انشاء حسابات اداريين اخرين بنفس صلاحياته او بصلاحيات اقل حسب رغبته
انشاء حساب اداري يتم من خلال لوحة التحكم فقط ولا يوجد نموذج او صفحة انشاء خاصة بهم
يمكن للاداري تعديل المتاجر ولكن لايمكنه حذفها كما لايمكنه تعديل حسابات الباعة او اضافة موظفين للمتاجر او ازالتهم لان هذه الصلاحيات خاصة بالمالك فقط
بعد ان يقوم البائع بإنشاء حساب يقوم الاداري بالتحقق من صحة البيانات التي ادخلها البائع عن طريق التواصل معه على رقم الهاتف الذي ادخله في نموذج التسجيل وبعد ان يتحقق من صحة البيانات يقوم بإدراج حساب تيليجرام البائع ليصله اشعارات عليه ثم يقوم بتفعيل الحساب ليتمكن البائع من تسجيل الدخول الى حسابه
======== هيكلية نظام المستخدمين في المشروع ======== 

User
└── UserProfile
Store
└── owner -> User
"""

# ===== لاتنسى تساوي ========
# 👉 Middleware يمنع أي شخص يدخل الصفحة الخطأ

class UserProfile(models.Model):
    USER_TYPES = [
        ('admin', 'إدارة'),
        ('vendor', 'بائع'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    
    name = models.CharField(
        max_length=255,
        verbose_name='الاسم الثنائي',
        help_text='أدخل الاسم الأول والاسم الأخير',
    )

    def __str__(self):
        return self.name
    
    @property
    def store(self):
        """
        يعيد المتجر المرتبط بالمستخدم الحالي.
        حالياً يتم إرجاع أول متجر فقط (لأن كل مستخدم يملك متجر واحد).
        سيتم تطويره لاحقاً لدعم اختيار المتجر النشط (Active Store).
        """
        return self.user.stores.first()
    
    class Meta:
        verbose_name = 'ملف شخصي'
        verbose_name_plural = 'الملفات الشخصية'

class Store(models.Model):    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stores',
        verbose_name='مالك المتجر',
    )
    name = models.CharField(max_length=255 , verbose_name="اسم المتجر", help_text="قم بإدخال اسم المتجر")
    
    STATUS_CHOICES = [
        ('pending', 'قيد  المراجعة'), 
        ('active', 'مُفعل'), 
        ('inactive', 'غير مُفعل')
    ]
    
    status = models.CharField(verbose_name='حالة المتجر', max_length=20, choices=STATUS_CHOICES, default='pending')
    logo = models.ImageField(upload_to='vendors/Stores/logos' , verbose_name="صورة لوجو المتجر", default='default/default_store_logo.png') 
    location = models.CharField(max_length=255 , verbose_name="الموقع", blank=True, help_text="قم بإدخال موقع المتجر الخاص بك \n يمكنك كتابة اسم المدينة فقط أو العنوان الكامل حسب رغبتك")
    check_orders = models.BooleanField(default=True, choices=[(False, 'غير مُفعل'), (True, 'مُفعل'),], verbose_name="تحقق من الطلبات " , help_text="في حال التفعيل سيقوم احد الموظفين لدينا من الاتصال بالزبون والتأكد من الطلب قبل ارسال اشعار اليك مما يقلل من الطلبات الوهمية")
    # جميع حقول السوشيال ميديا يتم اضافتها بعد انشاء الحساب وتفعيله الا رقم الهاتف يجب ادخاله اثناء انشاء الحساب لانه يستخدم في التواصل مع الادارة لتفعيل الحساب
    phone_number1 = models.CharField(verbose_name='رقم الهاتف',  max_length=20, help_text='قم بإدخال رقم الهاتف الخاص بمتجرك (ملاحظة : يجب ان يكون الرقم مربوطاً بواتساب لأننا سوف نقوم بالتواصل معك على واتساب لتفعيل حسابك) ')# يجب ان يقوم بإدخاله لان الادارة سوف تتواصل معه على هذا الرقم لتفعيل حسابه
    telegram = models.CharField(verbose_name='معرف التليجرام', blank=True, max_length=20, help_text="قم بإدخال رقم التليجرام الخاص بالمتجر حيث سوف يتم ارسال التنبيهات الخاصة بمتجرك من خلاله")
    facebook = models.URLField(verbose_name='فيسبوك', blank=True, help_text='قم بإدخال رابط بروفايل صفحة الفيسبوك الخاصة بمتجرك')
    instagram = models.URLField(verbose_name='انستاجرام', blank=True, help_text='قم بإدخال رابط بروفايل صفحة الانستاجرام الخاصة بمتجرك')
    tiktok = models.URLField(verbose_name='تيكتوك', blank=True, help_text='قم بإدخال رابط صفحة تيكتوك الخاصة بمتجرك')
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ آخر تحديث')
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'متجر'
        verbose_name_plural = 'المتاجر'
