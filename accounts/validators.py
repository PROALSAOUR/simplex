# ملف مخصص لدوال التحقق من البيانات في النماذج مثل التحقق من صحة رقم الهاتف او اليوزر نيم او اي تحقق اخر ممكن نحتاجه في المستقبل

import phonenumbers, re
from django.core.exceptions import ValidationError

def validate_username(username):    
    """هذه الدالة تتحقق من صحة اليوزر نيم بحيث لا يحتوي على مسافات ويحتوي فقط على أحرف إنجليزية وأرقام و_ ويكون طوله 4 أحرف على الأقل"""
    # منع المسافات
    if ' ' in username:
        raise ValidationError("اسم المستخدم لا يجب أن يحتوي على مسافات")
    #  فقط أحرف إنجليزية + أرقام + _
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("اسم المستخدم يجب أن يحتوي على أحرف إنجليزية وأرقام فقط")
    if len(username) < 4:
        raise ValidationError("اسم المستخدم يجب أن يكون 4 أحرف على الأقل")

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