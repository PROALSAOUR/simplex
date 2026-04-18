from django import forms
from django.contrib.auth.models import User
from .models import Vendor, Store, UserProfile
import phonenumbers
from django.core.exceptions import ValidationError
from .validators import validate_username, validate_phone_number


# نموذج انشاء حساب
class VendorRegisterForm(forms.ModelForm):
    # Vendor fields
    username = forms.CharField(
        label='المعرف',
        error_messages={
            'required': 'اسم المستخدم مطلوب',
            'invalid': 'اسم المستخدم غير صالح',
        }
    )
    password = forms.CharField(
        label='كلمة السر',
        widget=forms.PasswordInput,
        error_messages={
        'required': 'كلمة المرور مطلوبة',
        'invalid': 'كلمة المرور غير صالحة',
        }
    )
    confirm_password =forms.CharField(
    label='تأكيد كلمة السر',  
    widget=forms.PasswordInput,
        error_messages={
        'required': 'تأكيد كلمة المرور مطلوب',
        }
    )
    # Store fields
    store_name = forms.CharField(
        label='اسم المتجر',
        error_messages={
            'required': 'اسم المتجر مطلوب',
        }
    )
    location = forms.CharField(
        label='الموقع',
        error_messages={
            'required': 'موقع المتجر مطلوب',
        }
    )
    whatsapp = forms.CharField(
        label='رقم الواتساب',
        min_length=8,
        max_length=15,
        error_messages={
            'required': 'رقم واتساب مطلوب',
            'min_length': 'رقم الواتساب قصير جداً، يجب أن يكون 8 أرقام على الأقل.',
            'max_length': 'رقم الواتساب طويل جداً، الحد الأقصى 15 رقم.',
        }
    )
    class Meta:
        model = Vendor
        fields = ['name']
        error_messages = {
            'name': {
                'required': 'الاسم مطلوب',
            }
        }
    # password match
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("كلمتا المرور غير متطابقتين")
        return cleaned_data
    # username check
    def clean_username(self):
        # يتم التحقق بالقالب بشكل مباشر ايضا لكن يوجد تحقق هنا ايضا لضمان العمل بشكل سليم
        username = self.cleaned_data.get('username')
        validate_username(username)  # تحقق من صحة اليوزر نيم باستخدام الدالة في validators.py
        # منع التكرار
        if User.objects.filter(username=username).exists():
            raise ValidationError("اسم المستخدم موجود بالفعل")

        return username
    # whatsapp validation
    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get('whatsapp')
        whatsapp = validate_phone_number(whatsapp)  # تحقق من صحة رقم الهاتف باستخدام الدالة في validators.py
        # التحقق مما إذا كان الرقم مسجلاً لأحد المتاجر مسبقًا
        if Store.objects.filter(whatsapp=whatsapp).exists():
            raise ValidationError("رقم الهاتف مستخدم بالفعل. يرجى التواصل مع الدعم الفني في حال كنت متأكداً انك لم تسجل به مسبقاً لحل المشكلة.")
        return whatsapp

    def save(self, commit=True):
        # 1️⃣ إنشاء User
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )

        # 2️⃣ إنشاء Store
        store = Store.objects.create(
            name=self.cleaned_data['store_name'],
            location=self.cleaned_data['location'],
            whatsapp=self.cleaned_data['whatsapp']
        )

        # 3️⃣ إنشاء Vendor
        vendor = Vendor.objects.create(
            user=user,
            store=store,
            name=self.cleaned_data['name'],
            permission_level='owner'  # أول بائع يحصل على ملكية للمتجر
        )

        # 4️⃣ تحديد نوع الحساب
        UserProfile.objects.create(
            user=user,
            user_type='vendor'
        )
        return vendor

# نموذج تسجيل الدخول
class LoginForm(forms.Form):
    username = forms.CharField(
        label="اسم المستخدم",
        error_messages={
            'required': 'اسم المستخدم مطلوب',
        }
    )

    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput,
        error_messages={
            'required': 'كلمة المرور مطلوبة',
        }
    )
    
# نموذج انشاء موظف
class EmployeeRegisterForm(forms.ModelForm):
    # Vendor fields
    username = forms.CharField(
        error_messages={
            'required': ' المعرف مطلوب',
            'invalid': 'المعرف غير صالح',
        }
    )
    password = forms.CharField(
        label='كلمة السر',
        widget=forms.PasswordInput,
        error_messages={
        'required': 'كلمة المرور مطلوبة',
        'invalid': 'كلمة المرور غير صالحة',
        }
    )
    confirm_password =forms.CharField(
    label='تأكيد كلمة السر',
    widget=forms.PasswordInput,
        error_messages={
        'required': 'تأكيد كلمة المرور مطلوب',
        }
    )
    class Meta:
        model = Vendor
        fields = ['name', 'permission_level']
        error_messages = {
            'name': {
                'required': 'الاسم مطلوب',
            }
        }
        
    def __init__(self, *args, **kwargs): # استقبال كائن المتجر عند استدعاء الفورم
        # استقبل المتجر من الـ view
        self.store = kwargs.pop('store', None)
        super().__init__(*args, **kwargs)
        excluded_choice = 'owner'  # استثناء خيار المالك من خيارات الصلاحية عند انشاء موظف
        self.fields['permission_level'].choices = [
            choice for choice in self.fields['permission_level'].choices
            if choice[0] != excluded_choice
        ]

    # password match
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("كلمتا المرور غير متطابقتين")
        return cleaned_data
    # username check
    def clean_username(self):
        # يتم التحقق بالقالب بشكل مباشر ايضا لكن يوجد تحقق هنا ايضا لضمان العمل بشكل سليم
        username = self.cleaned_data.get('username')
        validate_username(username)  # تحقق من صحة اليوزر نيم باستخدام الدالة في validators.py
        return username
        

    def save(self, commit=True):
        # 1️⃣ إنشاء User
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )

        # 3️⃣ إنشاء Vendor
        vendor = Vendor.objects.create(
            user=user,
            store=self.store, # هنا المشكلة
            name=self.cleaned_data['name'],
            permission_level=self.cleaned_data['permission_level']  
        )

        # 4️⃣ تحديد نوع الحساب
        UserProfile.objects.create(
            user=user,
            user_type='vendor'
        )
        return vendor
