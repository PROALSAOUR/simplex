# ملف مخصص لدوال التحقق من البيانات في النماذج مثل التحقق من صحة رقم الهاتف او اليوزر نيم او اي تحقق اخر ممكن نحتاجه في المستقبل

import phonenumbers, re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

def validate_username(username, current_user_id=None):    
    """هذه الدالة تتحقق من صحة اليوزر نيم بحيث لا يحتوي على مسافات ويحتوي فقط على أحرف إنجليزية وأرقام و_ ويكون طوله 4 أحرف على الأقل"""
    # منع المسافات
    if ' ' in username:
        raise ValidationError("اسم المستخدم لا يجب أن يحتوي على مسافات")
    #  فقط أحرف إنجليزية + أرقام + _
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("اسم المستخدم يجب أن يحتوي على أحرف إنجليزية وأرقام فقط")
    if len(username) < 4:
        raise ValidationError("اسم المستخدم يجب أن يكون 4 أحرف على الأقل")
    # منع استعمال يوزر مستعمل مسبقا
    qs = User.objects.filter(username=username) 
    if current_user_id is not None: # لو كان عم يسأل بدالة تعديل الحساب عن المعرف الخاص به 
        qs = qs.exclude(pk=current_user_id)
    if qs.exists():
        raise ValidationError("هذا المعرف مستعمل مسبقًا، رجاءً اختر معرفاً آخر.")

def validate_phone_number(phone_number):
    """هذه الدالة تتحقق من صحة رقم الهاتف بحيث يكون رقم ليبي صالح ويتم تحويله لصيغة دولية موحدة"""
    try:
        parsed_phone = phonenumbers.parse(phone_number, 'LY') # يتم قبول ارقام ليبية فقط
        if not phonenumbers.is_valid_number(parsed_phone):
            raise ValidationError("رقم الهاتف غير صالح.")
        
        # تحويل الرقم لصيغة موحدة دولية (+218...)
        phone_number = phonenumbers.format_number(
            parsed_phone,
            phonenumbers.PhoneNumberFormat.E164
        )
            
    except phonenumbers.NumberParseException:
        raise ValidationError("يرجى إدخال رقم هاتف صحيح.")
    except Exception:
        raise ValidationError( 'حدث خطأ غير متوقع، الرجاء المحاولة لاحقًا')
        
    return phone_number

def get_redirect_url_for_user(user):
    """
    دالة تستقبل كائن مستخدم وتتحقق من نوعه وتعيد رابط التوجيه المناسب وفقا لذلك
    """
    
    try:
        user_profile = user.userprofile
    except:
        return None

    if user_profile.user_type == 'vendor':
        if hasattr(user, 'vendor'):
            store = user.vendor.store
            if store.status == 'pending':
                return 'accounts:account_under_review'
            return 'vendors:vendor_dashboard'

    elif user_profile.user_type == 'admin':
        return 'admin_dashboard'

    return None
        