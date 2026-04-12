from django.db import models
from django.contrib.auth.models import User

"""
======== بالنسبة للبائع ========
تسجيل الدخول يتم من خلال اليوزرنيم والباسورد الخاصين بالبائع حيث يتم جلب المتجر المرتبط بهم والدخول اليه
انشاء حساب بنموذج واحد يوجد به حقول البائع والمتجر معا لتسهيل عملية التسجيل وربط البائع بالمتجر مباشرة عند انشاء الحساب
يتم اعطاء اقصى صلاحية لأول بائع يتم انشائه للمتجر
يمكن للبائع ذو اقصى صلاحية اضافة او ازالة بائعين اخرين للمتجر وتحديد صلاحياتهم
======== اما بالنسبة للإدارة ========
تسجيل الدخول يتم من خلال اليوزرنيم والباسورد الخاصين بالإدارة حيث يتم تسجيل الدخول من نفس الصفحة التي يسجل بها الباعة دخولهم ولكن يتم تمييزهم من خلال نوع المستخدم في ملف البروفايل الخاص بهم
يمكن للاداري ذو صلاحية السوبريوزر  انشاء حسابات اداريين اخرين بنفس صلاحياته او بصلاحيات اقل حسب رغبته
انشاء حساب اداري يتم من خلال لوحة التحكم فقط ولا يوجد نموذج او صفحة انشاء خاصة بهم

======== هيكلية نظام المستخدمين في المشروع ======== 
User (Django)
 ├── UserProfile (admin / vendor)
 │
 ├── Vendor (if vendor)
 │     └── Store
 │
 └── Admin (no model needed)
"""

# ===== لاتنسى تساوي ========
# 👉 Middleware يمنع أي شخص يدخل الصفحة الخطأ
# 👉 Decorator مثل @admin_only و @vendor_only

class UserProfile(models.Model):
    USER_TYPES = [
        ('admin', 'إدارة'),
        ('vendor', 'بائع'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
    
    class Meta:
        verbose_name = 'ملف شخصي'
        verbose_name_plural = 'الملفات الشخصية'

class Store(models.Model):
    slug = models.SlugField(max_length=100, unique=True , verbose_name='slug', null=True) # هذا الحقل يستخدم في الروابط لتحديد المتجر بشكل فريد، يتم انشاءه من قبل الادارة قبل قبول وتفعيل المتجر 
    name = models.CharField(max_length=255 , verbose_name="اسم المتجر", help_text="قم بإدخال اسم المتجر")
    status = models.CharField(verbose_name='حالة المتجر', max_length=20, choices=[('pending', 'قيد  المراجعة'), ('active', 'مُفعل'), ('inactive', 'غير مُفعل')], default='pending')
    logo = models.ImageField(upload_to='vendors/Stores/logos' , verbose_name="صورة لوجو المتجر") # عدلها بعدين بحيث يكون فيه صورة افتراضية
    location = models.CharField(max_length=255 , verbose_name="الموقع", help_text="قم بإدخال موقع المتجر الخاص بك \n يمكنك كتابة اسم المدينة فقط أو العنوان الكامل حسب رغبتك")
    telegram = models.CharField(verbose_name='رقم التليجرام', max_length=20, help_text="قم بإدخال رقم التليجرام الخاص بالمتجر حيث سوف يتم ارسال التنبيهات الخاصة بمتجرك من خلاله")
    facebook = models.URLField(verbose_name='فيسبوك', blank=True, help_text='قم بإدخال رابط بروفايل صفحة الفيسبوك الخاصة بمتجرك')
    instagram = models.URLField(verbose_name='انستاجرام', blank=True, help_text='قم بإدخال رابط بروفايل صفحة الانستاجرام الخاصة بمتجرك')
    tiktok = models.URLField(verbose_name='تيكتوك', blank=True, help_text='قم بإدخال رابط صفحة تيكتوك الخاصة بمتجرك')
    whatsapp = models.CharField(verbose_name='رقم الواتساب', blank=True, max_length=20, help_text='قم بإدخال رقم الواتساب الخاص بالمتجر')
    phone_number1 = models.CharField(verbose_name='رقم الاتصال', null=True, max_length=20, help_text='قم بإدخال رقم الهاتف الذي تريد من الزبائن الاتصال بك من خلاله')
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='تاريخ الإنشاء')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'متجر'
        verbose_name_plural = 'المتاجر'

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='اسم المستخدم', help_text='قم بإدخال اسم المستخدم الخاص بك')
    permission_level = models.CharField(verbose_name='مستوى الصلاحيات', max_length=20, choices=[('view',  'عرض فقط'), ('edit', 'عرض وتعديل'), ('full', 'تحكم كامل (عرض + تعديل + حذف)')], default='view', help_text='قم بتحديد مستوى الصلاحية الخاص بك \n  عرض فقط: يمكنك عرض المنتجات والطلبات ولكن لا يمكنك تعديلها أو حذفها \n عرض وتعديل: يمكنك عرض وتعديل المنتجات والطلبات ولكن لا يمكنك حذفها \n  تحكم كامل: يمكنك عرض وتعديل وحذف المنتجات والطلبات والأرباح')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='vendors', verbose_name='المتجر')
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='تاريخ الإنشاء')
    
    def __str__(self):
        return f"{self.store} - {self.name}"
    
    class Meta:
        verbose_name = 'بائع'
        verbose_name_plural = 'البائعين'
    
