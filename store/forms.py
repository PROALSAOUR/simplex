from django import forms
from .models import Product


class ProductRegisterForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'thumbnail_img', 'description', 'show', 'purchase_price', 'price', 'offer', 'offer_price', 'free_delivery', 'has_sizes', 'type', 'gender', 'max_quantity_per_order']
        
    def __init__(self, *args, **kwargs): # استقبال كائن المتجر عند استدعاء الفورم
        # استقبل المتجر من الـ view
        self.store = kwargs.pop('store', None)
        super().__init__(*args, **kwargs)
        
        
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
            max_quantity_per_order=self.cleaned_data['max_quantity_per_order']
        )
        return product
        
