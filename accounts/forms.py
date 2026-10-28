from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from Project.utils import compress_image
from Project.validators import validate_image_file
from accounts.models import Store, UserProfile
from accounts.validators import validate_username, validate_phone_number

# نموذج انشاء حساب
class StoreRegisterForm(forms.ModelForm):
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
        label='كلمة المرور',
        help_text = "كلمة المرور يجب أن تكون قوية وتتكون من 4 أحرف على الأقل، وتشمل حروفًا وأرقامًا \n (في حال نسيان كلمة المرور سوف يتوجب عليك التواصل يدويا مع خدمة العملاء لتغييرها لذا يرجى حفظها جيدا.)",
        widget=forms.PasswordInput,
        error_messages={
        'required': 'كلمة المرور مطلوبة',
        'invalid': 'كلمة المرور غير صالحة',
        }
    )
    confirm_password =forms.CharField(
    label='تأكيد كلمة المرور',  
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
        model = UserProfile
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
            owner=user,
            name=self.cleaned_data['store_name'],
            phone_number1=self.cleaned_data['phone_number1']
        )

        # 4️⃣ تحديد نوع الحساب
        UserProfile.objects.create(
            user=user,
            user_type='vendor',
            name=self.cleaned_data['name'],
        )
        return user

# نموذج تسجيل الدخول
class LoginForm(forms.Form):
    username = forms.CharField(
        label="المعرف",
        help_text="ادخل المعرف الذي استخدمته عند انشاء حسابك",
        error_messages={
            'required': 'المعرف مطلوب',
        }
    )

    password = forms.CharField(
        label="كلمة المرور",
        help_text="أدخل كلمة المرور الخاصة بك",
        widget=forms.PasswordInput,
        error_messages={
            'required': 'كلمة المرور مطلوبة',
        }
    )

# نموذج تعديل حساب مستخدم ( الاسم + المعرف)
class AccountUpdateForm(forms.ModelForm):
    
    username = forms.CharField(
        label='المعرف',
        help_text = 'المعرف هو اسم المستخدم الذي ستسجل به الدخول. يجب أن يتكون من أحرف إنجليزية وأرقام فقط، ولا يحتوي على فراغات.',
        error_messages={
            'required': 'المعرف  مطلوب',
            'invalid': 'اسم المستخدم غير صالح',
        },
        widget=forms.TextInput(attrs={
            'id': 'username',
            'placeholder': '(مثل: example1)'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ['name']
        error_messages = {
            'name': {
                'required': 'الاسم مطلوب',
            }
        }
    
    def __init__(self, *args, user=None, **kwargs):
        # الاحتفاظ بالمستخدم للتحقق من كلمة المرور والمعرف.
        super().__init__(*args, **kwargs)
        self.user = user

        if user:
            self.fields['name'].initial = user.userprofile.name
            self.fields['username'].initial = user.username
            
    def clean_username(self):
        # التحقق من صلاحية المعرف وعدم استخدامه من حساب آخر.
        username = self.cleaned_data['username'].strip()

        validate_username(username, self.user.pk)

        return username

# نموذج تعديل كلمة مرور مستخدم 
class PasswordChangeForm(forms.Form):
    
    # حقل كلمة المرور القديمة.
    old_password = forms.CharField(
        label='كلمة المرور الحالية',
        required=False,
        help_text='أدخل كلمة المرور الحالية.',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': 'كلمة المرور الحالية',
        }),
        error_messages={
            'required': 'كلمة المرور الحالية مطلوبة.',
        }
    )
    # حقل كلمة المرور الجديدة.
    new_password = forms.CharField(
        label='كلمة المرور الجديدة',
        required=False,
        help_text=(
            'يجب أن تتكون من 4 أحرف على الأقل، '
        ),
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'كلمة المرور الجديدة',
        }),
        error_messages={
            'required': 'كلمة المرور الجديدة مطلوبة.',
        }
    )
    # تأكيد كلمة المرور الجديدة.
    confirmnew_password = forms.CharField(
        label='تأكيد كلمة المرور',
        required=False,
        help_text='أعد إدخال كلمة المرور الجديدة.',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'تأكيد كلمة المرور الجديدة',
        }),
        error_messages={
            'required': 'تأكيد كلمة المرور مطلوب.',
        }
    )
            
    def __init__(self, *args, user=None, **kwargs):
        # الاحتفاظ بالمستخدم للتحقق من كلمة المرور الحالية.
        super().__init__(*args, **kwargs)
        self.user = user
                
    def clean(self):
        # التحقق من جميع الحقول المرتبطة بتغيير كلمة المرور.
        cleaned_data = super().clean()

        old_password = cleaned_data.get('old_password', '')
        new_password = cleaned_data.get('new_password', '')
        confirm_password = cleaned_data.get('confirmnew_password', '')

        # السماح بإرسال الفورم دون تغيير كلمة المرور.
        if not any((old_password, new_password, confirm_password)):
            return cleaned_data

        # التأكد من وجود كلمة المرور القديمة وصحتها.
        if not old_password:
            self.add_error(
                'old_password',
                'يرجى إدخال كلمة المرور القديمة.'
            )
        elif not self.user or not self.user.check_password(old_password):
            self.add_error(
                'old_password',
                'كلمة المرور القديمة غير صحيحة.'
            )

        # التحقق من كلمة المرور الجديدة.
        if not new_password:
            self.add_error(
                'new_password',
                'يرجى إدخال كلمة المرور الجديدة.'
            )
        elif len(new_password) < 4:
            self.add_error(
                'new_password',
                'يجب أن تتكون كلمة المرور من 4 أحرف على الأقل.'
            )

        # التحقق من تأكيد كلمة المرور.
        if not confirm_password:
            self.add_error(
                'confirmnew_password',
                'يرجى تأكيد كلمة المرور الجديدة.'
            )
        elif new_password and new_password != confirm_password:
            self.add_error(
                'confirmnew_password',
                'كلمتا المرور غير متطابقتين.'
            )

        return cleaned_data

    @property
    def changes_password(self):
        # تحديد ما إذا كانت هناك كلمة مرور جديدة صالحة في بيانات الفورم.
        return bool(
            self.cleaned_data.get('new_password')
            if hasattr(self, 'cleaned_data')
            else False
        )
# نموذج تعديل جميع بيانات المتجر من نموذج واحد
class StoreUpdateForm(forms.ModelForm):
    check_orders = forms.BooleanField(
        required=False,
        label=Store._meta.get_field('check_orders').verbose_name,
        help_text=Store._meta.get_field('check_orders').help_text,
    )
    class Meta:
        model = Store
        fields = [
            'name',
            'location',
            'logo',
            'check_orders',
            'facebook',
            'instagram',
            'tiktok',
        ]

    def clean_name(self):
        # التحقق من صحة اسم المتجر
        store_name = self.cleaned_data["name"].strip()

        if store_name.isdigit():
            raise ValidationError("اسم المتجر لا يجب أن يكون رقماً فقط.")

        if len(store_name) < 3:
            raise ValidationError("اسم المتجر يجب أن يكون 3 أحرف أو أكثر.")

        return store_name


    def clean_logo(self):
        # ضغط والتحقق من صورة شعار المتجر
        logo = self.cleaned_data.get("logo")

        # إذا لم يرفع المستخدم صورة جديدة نحتفظ بالصورة الحالية
        if not logo:
            return self.instance.logo

        compressed_logo = compress_image(logo)

        if not validate_image_file(compressed_logo):
            raise ValidationError("الصورة غير صالحة أو حجمها كبير.")

        return compressed_logo

    def clean_check_orders(self):
            # تحويل قيمة checkbox إلى True أو False بشكل صحيح
            value = self.cleaned_data.get('check_orders')
    
            return bool(value)
            
class StoreAdminUpdateForm(StoreUpdateForm):
    class Meta(StoreUpdateForm.Meta):
        # نموذج الإدارة يحتوي أيضًا على حالة المتجر ورقم الهاتف والتليجرام
        fields = StoreUpdateForm.Meta.fields + [
            'status',
            'telegram',
            'phone_number1',
        ]

    def clean_phone_number1(self):
        # التحقق من رقم الهاتف وعدم تكراره في متجر آخر
        phone_number1 = self.cleaned_data.get('phone_number1')

        if not phone_number1:
            return phone_number1

        phone_number1 = validate_phone_number(phone_number1)

        existing_stores = Store.objects.filter(
            phone_number1=phone_number1
        )

        if self.instance.pk:
            existing_stores = existing_stores.exclude(
                pk=self.instance.pk
            )

        if existing_stores.exists():
            raise ValidationError(
                "رقم الهاتف مستخدم بالفعل. يرجى التواصل مع الدعم الفني في حال كنت متأكداً أن الرقم غير مسجل مسبقاً."
            )

        return phone_number1        