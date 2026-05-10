from django.db import models
from django.contrib.auth.models import User

"""
======== بالنسبة للبائع ========
تسجيل الدخول يتم من خلال اليوزرنيم والباسورد الخاصين بالبائع حيث يتم جلب المتجر المرتبط بهم والدخول اليه
يمكن تسجيل الدخول فقط ان كانت حالة المتجر  (مفعل او غير مفعل ) ولا يمكن تسجيل الدخول اذا كانت حالة الحساب قيد المراجعة لأن هذا يعني ان الادارة لم تتحقق من بيانات الحساب بعد
انشاء حساب بنموذج واحد يوجد به حقول البائع والمتجر معا لتسهيل عملية التسجيل وربط البائع بالمتجر مباشرة عند انشاء الحساب
يتم اعطاء اقصى صلاحية وهي المالك لأول بائع يتم انشائه للمتجر
يمكن فقط للمالك وهو ذو اقصى صلاحية اضافة او ازالة بائعين اخرين للمتجر وتحديد صلاحياتهم
يمكن للمستخدم ذو التحكم الكامل اضافة او ازالة او تعديل اي شيء بإستثناء الموظفين حيث انها خاصية خاصة بالمالك فقط
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
    slug = models.SlugField(max_length=100, unique=False , verbose_name='slug', blank=True , help_text=" اسم المتجر باللغة الانجليزية وبدون فراغات ") # هذا الحقل يستخدم في الروابط لتحديد المتجر بشكل فريد، يتم انشاءه من قبل الادارة قبل قبول وتفعيل المتجر 
    name = models.CharField(max_length=255 , verbose_name="اسم المتجر", help_text="قم بإدخال اسم المتجر")
    status = models.CharField(verbose_name='حالة المتجر', max_length=20, choices=[('pending', 'قيد  المراجعة'), ('active', 'مُفعل'), ('inactive', 'غير مُفعل')], default='pending')
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
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'متجر'
        verbose_name_plural = 'المتاجر'


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='الاسم الثنائي', help_text='قم بإدخال اسمك الثنائي (الاسم الأول والاسم الأخير)')
    permission_level = models.CharField(verbose_name='مستوى الصلاحيات', max_length=20, choices=[('edit', 'عرض وتعديل'), ('full', 'تحكم كامل (عرض + تعديل + حذف)'), ('owner', 'مالك المتجر')], default='edit', help_text='قم بتحديد مستوى الصلاحية الخاص بك \n عرض وتعديل: يمكنك عرض وتعديل المنتجات والطلبات ولكن لا يمكنك حذفها \n  تحكم كامل: يمكنك عرض وتعديل وحذف المنتجات والطلبات والأرباح \n مالك المتجر : بإمكانه التحكم بكل شيء')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='vendors', verbose_name='المتجر')
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='تاريخ الإنشاء')
    
    def __str__(self):
        return f"{self.store} - {self.name}"
    
    class Meta:
        verbose_name = 'بائع'
        verbose_name_plural = 'البائعين'
    
