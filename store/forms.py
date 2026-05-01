from django import forms
from .validators import validate_image_file
from .models import Product
from django.core.exceptions import ValidationError


class ProductRegisterForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'thumbnail_img', 'description', 'show', 'purchase_price', 'price', 'offer', 'offer_price', 'free_delivery', 'has_sizes', 'type', 'gender']
        
    def __init__(self, *args, **kwargs): # استقبال كائن المتجر عند استدعاء الفورم
        # استقبل المتجر من الـ view
        self.store = kwargs.pop('store', None)
        super().__init__(*args, **kwargs)
        # السعر بعد التخفيض ليس مطلوبا إلا عندما يتم تنشيط خيار التخفيض
        self.fields['offer_price'].required = False
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
        if image:
            is_valid = validate_image_file(image)
            if not is_valid:
                raise ValidationError("الصورة غير صالحة أو حجمها كبير")
        return image
        
    def save(self, commit=True):
        product = Product.objects.create(
            store = self.store,
            name=self.cleaned_data['name'],
            thumbnail_img=self.cleaned_data['thumbnail_img'],
            description=self.cleaned_data['description'],
            show=self.cleaned_data['show'],
            purchase_price=self.cleaned_data['purchase_price'],
            price=self.cleaned_data['price'],
            offer=self.cleaned_data['offer'],
            offer_price=self.cleaned_data['offer_price'],
            free_delivery=self.cleaned_data['free_delivery'],
            has_sizes=self.cleaned_data['has_sizes'],
            type=self.cleaned_data['type'],
            gender=self.cleaned_data['gender'],
        )
        return product
        
