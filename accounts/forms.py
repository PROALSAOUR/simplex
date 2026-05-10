from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from Project.utils import compress_image
from store.validators import validate_image_file
from accounts.models import Vendor, Store, UserProfile
from accounts.validators import validate_username, validate_phone_number


# نموذج انشاء حساب
class VendorRegisterForm(forms.ModelForm):
    # Vendor fields
    username = forms.CharField(
        label='المعرف',
        help_text = 'المعرف هو اسم المستخدم الذي ستسجل به الدخول. يجب أن يتكون من أحرف إنجليزية وأرقام فقط، ولا يحتوي على فراغات.',
        error_messages={
            'required': 'اسم المستخدم مطلوب',
            'invalid': 'اسم المستخدم غير صالح',
        },
        widget=forms.TextInput(attrs={
            'placeholder': '(مثل: example1)'
        })
    )
    password = forms.CharField(
        label='كلمة السر',
        help_text = "كلمة السر يجب أن تكون قوية وتتكون من 4 أحرف على الأقل، وتشمل حروفًا وأرقامًا \n (في حال نسيان كلمة المرور سوف يتوجب عليك التواصل يدويا مع خدمة العملاء لتغييرها لذا يرجى حفظها جيدا.)",
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
        help_text = 'اسم المتجر الذي سيظهر للعملاء. يمكنك تعديله لاحقًا من إعدادات المتجر.',
        error_messages={
            'required': 'اسم المتجر مطلوب',
        }
    )
    phone_number1 = forms.CharField(
        label='رقم الهاتف',
        help_text = 'رقم الهاتف الذي سوف نتواصل معك من خلاله لتفعيل حسابك,ملاحظة: يجب ان يكون مربوطاً بواتساب.',
        min_length=8,
        max_length=15,
        error_messages={
            'required': 'رقم الهاتف مطلوب',
            'min_length': 'رقم الهاتف  قصير جداً، يجب أن يكون 8 أرقام على الأقل.',
            'max_length': 'رقم الهاتف طويل جداً، الحد الأقصى 15 رقم.',
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
    def clean_store_name(self):
        store_name = self.cleaned_data["store_name"].strip()

        if store_name.isdigit():
            raise ValidationError("اسم المتجر لا يجب أن يكون رقماً فقط.")

        if len(store_name) < 3:
            raise ValidationError("اسم المتجر  يجب أن يكون 3 أحرف أو أكثر.")

        return store_name
    
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
    # phone_number1 validation
    def clean_phone_number1(self):
        phone_number1 = self.cleaned_data.get('phone_number1')
        phone_number1 = validate_phone_number(phone_number1)  # تحقق من صحة رقم الهاتف باستخدام الدالة في validators.py
        # التحقق مما إذا كان الرقم مسجلاً لأحد المتاجر مسبقًا
        if Store.objects.filter(phone_number1=phone_number1).exists():
            raise ValidationError("رقم الهاتف مستخدم بالفعل. يرجى التواصل مع الدعم الفني في حال كنت متأكداً انك لم تسجل به مسبقاً لحل المشكلة.")
        return phone_number1

    def save(self, commit=True):
        # 1️⃣ إنشاء User
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )

        # 2️⃣ إنشاء Store
        store = Store.objects.create(
            name=self.cleaned_data['store_name'],
            phone_number1=self.cleaned_data['phone_number1']
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

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if name.isdigit():
            raise ValidationError("اسم الموظف لا يجب أن يكون رقماً فقط.")

        if len(name) < 3:
            raise ValidationError("اسم الموظف  يجب أن يكون 3 أحرف أو أكثر.")

        return name
    

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
            store=self.store, 
            name=self.cleaned_data['name'],
            permission_level=self.cleaned_data['permission_level']  
        )

        # 4️⃣ تحديد نوع الحساب
        UserProfile.objects.create(
            user=user,
            user_type='vendor'
        )
        return vendor

# نموذج تعديل بيانات المتجر الاساسية
class StoreBasicForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'location', 'check_orders']
        
    def clean_name(self):
        store_name = self.cleaned_data["name"].strip()

        if store_name.isdigit():
            raise ValidationError("اسم المتجر لا يجب أن يكون رقماً فقط.")

        if len(store_name) < 3:
            raise ValidationError("اسم المتجر  يجب أن يكون 3 أحرف أو أكثر.")

        return store_name
    
    def clean_location(self):
        location = self.cleaned_data["location"].strip()

        if location.isdigit():
            raise ValidationError("موقع المتجر لا يجب أن يكون رقماً فقط.")

        if len(location) < 3:
            raise ValidationError("موقع المتجر  يجب أن يكون 3 أحرف أو أكثر.")

        return location
        
# نموذج تحديث حسابات المتجر الاجتماعية
class StoreSocialForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['telegram', 'facebook', 'instagram', 'tiktok']
        
# نموذج تحديث لوجو المتجر 
class StoreLogoForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['logo']

    def clean_logo(self):
        logo = self.cleaned_data.get("logo")
        if not logo:
            return logo 
        
        compressed_logo = compress_image(logo)
        if not validate_image_file(compressed_logo):
            raise ValidationError("الصورة غير صالحة أو حجمها كبير")
        return compressed_logo
        
