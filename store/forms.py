from django import forms
from store.validators import validate_image_file
from store.models import *
from django.core.exceptions import ValidationError
from Project.utils import compress_image

class ProductRegisterForm(forms.ModelForm):
    images_order = forms.CharField(required=False, widget=forms.HiddenInput())
    deleted_images = forms.CharField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = Product
        fields = ['name', 'thumbnail_img', 'description', 'is_visible', 'purchase_price', 'price', 'offer', 'offer_price', 'free_delivery', 'type', 'gender', 'max_quantity_per_order']
        
    def __init__(self, *args, **kwargs): # استقبال كائن المتجر عند استدعاء الفورم
        # استقبل المتجر من الـ view
        self.store = kwargs.pop('store', None)
        super().__init__(*args, **kwargs)
        # السعر بعد التخفيض ليس مطلوبا إلا عندما يتم تنشيط خيار التخفيض
        self.fields['offer_price'].required = False
        self.fields['max_quantity_per_order'].required = False
        self.fields['offer_price'].widget.attrs['placeholder'] = 'إذا كان هناك تخفيض، أدخل السعر بعد التخفيض'
        
    def clean_offer_price(self):
        offer = self.cleaned_data.get('offer')
        offer_price = self.cleaned_data.get('offer_price')
        price = self.cleaned_data.get('price')

        if offer:
            if offer_price is None:
                raise ValidationError("يرجى إدخال سعر التخفيض")
            if price is not None and offer_price >= price:
                raise ValidationError("سعر التخفيض يجب أن يكون أقل من السعر الأصلي")
            return offer_price

        return offer_price or 0
        
    def clean_thumbnail_img(self):
        image = self.cleaned_data.get("thumbnail_img")
        
        # إذا ما رفع صورة جديدة → خلي القديمة كما هي
        if not image or isinstance(image, str):
            return self.instance.thumbnail_img

        # إذا رفع صورة جديدة → اضغطها
        compressed_image = compress_image(image)
        
        if not validate_image_file(compressed_image):
            raise ValidationError("الصورة غير صالحة أو حجمها كبير")
        
        return compressed_image
        
    def save(self, commit=True):
        # خذ الكائن (سواء جديد أو للتعديل)
        product = super().save(commit=False)
        product.status = "checking" # عند اجراء اي تعديل اعادة حالة المنتج الى جاري المراجعة

        # إذا كان كائن جديد (إنشاء)
        if not product.pk:
            product.store = self.store

        # حفظ الكائن
        if commit:
            product.save()

        return product
        
