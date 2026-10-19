# نموذج تعديل جميع بيانات المدينة من نموذج واحد
from django import forms
from admins.models import City
from django.core.exceptions import ValidationError

class CityUpdateForm(forms.ModelForm):
    active = forms.BooleanField(
        required=False,
        initial=True,
        label=City._meta.get_field('active').verbose_name,
        help_text=City._meta.get_field('active').help_text,
    )
    class Meta:
        model = City
        fields = [
            'name',
            'active',
            'priority',
        ]

    def clean_name(self):
        # التحقق من صحة اسم المدينة
        city_name = self.cleaned_data["name"].strip()

        if city_name.isdigit():
            raise ValidationError("اسم المدينة لا يجب أن يكون رقماً فقط.")

        if len(city_name) < 3:
            raise ValidationError("اسم المدينة يجب أن يكون 3 أحرف أو أكثر.")

        return city_name


    def clean_active(self):
        # تحويل قيمة checkbox إلى True أو False بشكل صحيح
        value = self.cleaned_data.get('active')
        return bool(value)
    