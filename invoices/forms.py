from django import forms
from decimal import Decimal
from .models import Invoice


class InvoiceDiscountForm(forms.Form):
    # التحقق من قيمة الخصم ومقارنتها بقيمة العمولة
    discount = forms.DecimalField(
        required=True,
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=12,
        error_messages={
            "required": "يرجى إدخال قيمة الخصم.",
            "invalid": "يرجى إدخال قيمة خصم صالحة.",
            "min_value": "يجب أن تكون قيمة الخصم أكبر من أو تساوي صفر.",
        },
    )

    def __init__(self, *args, commission_value=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.commission_value = commission_value

    def clean_discount(self):
        # التأكد من أن الخصم لا يتجاوز قيمة العمولة
        discount = self.cleaned_data["discount"]

        if (
            self.commission_value is not None
            and discount > self.commission_value
        ):
            raise forms.ValidationError(
                "يجب أن تكون قيمة الخصم أقل من أو تساوي قيمة العمولة."
            )

        return discount


class InvoiceStatusForm(forms.Form):
    # التحقق من أن الحالة المختارة ضمن حالات الفاتورة
    status = forms.ChoiceField(
        choices=Invoice.STATUS_CHOICES,
        required=True,
        error_messages={
            "required": "يرجى اختيار حالة.",
            "invalid_choice": "يرجى اختيار حالة صحيحة.",
        },
    )

