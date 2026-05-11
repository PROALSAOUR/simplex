from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.validators import validate_phone_number
from orders.models import Order, OredrItem
from store.models import Product, ProductColor, ProductSize


class OrderRegisterForm(forms.ModelForm):
    """Customer data form used when creating an order."""

    class Meta:
        model = Order
        fields = ["customer_name", "customer_phone", "customer_location", "note"]

    def __init__(self, *args, store=None, is_vendor=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.store = store
        self.is_vendor = is_vendor
        self.fields["note"].required = False

        if not is_vendor:
            self.fields.pop("note")

    def clean_customer_phone(self):
        return validate_phone_number(self.cleaned_data["customer_phone"])

    def clean_customer_name(self):
        customer_name = self.cleaned_data["customer_name"].strip()

        if customer_name.isdigit():
            raise ValidationError("اسم المستلم لا يجب أن يكون رقما فقط.")

        if len(customer_name) < 4:
            raise ValidationError("اسم المستلم يجب أن يكون 4 أحرف أو أكثر.")

        return customer_name

    def clean_customer_location(self):
        customer_location = self.cleaned_data["customer_location"].strip()

        if customer_location.isdigit():
            raise ValidationError("العنوان لا يجب أن يكون رقما فقط.")

        if len(customer_location) < 3:
            raise ValidationError("العنوان يجب أن يكون 3 أحرف أو أكثر.")

        return customer_location


class OrderItemRegisterForm(forms.ModelForm):
    """نموذج عنصر الطلب"""

    product = forms.ModelChoiceField(queryset=Product.objects.none())
    product_color = forms.ModelChoiceField(queryset=ProductColor.objects.none())
    product_size = forms.ModelChoiceField(
        queryset=ProductSize.objects.none(),
        required=False,
    )

    class Meta:
        model = OredrItem
        fields = ["product", "product_color", "product_size", "qty"]

    def __init__(self, *args, store=None, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.store = store

        products = Product.objects.filter(is_visible=True)
        if store is not None:
            products = products.filter(store=store)
        self.fields["product"].queryset = products

        colors = ProductColor.objects.filter(available=True, product__is_visible=True)
        if product is not None:
            colors = colors.filter(product=product)
        elif store is not None:
            colors = colors.filter(product__store=store)
        self.fields["product_color"].queryset = colors

        sizes = ProductSize.objects.filter(available=True, product_color__available=True)
        if product is not None:
            sizes = sizes.filter(product_color__product=product)
        elif store is not None:
            sizes = sizes.filter(product_color__product__store=store)
        self.fields["product_size"].queryset = sizes

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        product_color = cleaned_data.get("product_color")
        product_size = cleaned_data.get("product_size")
        qty = cleaned_data.get("qty")

        if product and self.store and product.store_id != self.store.id:
            self.add_error("product", "هذا المنتج لا يتبع المتجر المحدد.")

        if product and product_color:
            if product_color.product_id != product.id:
                self.add_error("product_color", "هذا اللون لا يتبع المنتج المحدد.")
            elif not product_color.available:
                self.add_error("product_color", "هذا اللون غير متوفر حاليا.")

        if product_color:
            has_sizes = product_color.sizes.filter(available=True).exists()
            if has_sizes and not product_size:
                self.add_error("product_size", "يرجى اختيار المقاس.")

        if product_color and product_size:
            if product_size.product_color_id != product_color.id:
                self.add_error("product_size", "هذا المقاس لا يتبع اللون المحدد.")
            elif not product_size.available:
                self.add_error("product_size", "هذا المقاس غير متوفر حاليا.")

        if product and qty and qty > product.max_quantity_per_order:
            self.add_error(
                "qty",
                f"الكمية القصوى لهذا المنتج هي {product.max_quantity_per_order}.",
            )

        return cleaned_data

    def save(self, commit=True, order=None):
        if order is None:
            raise ValueError("OrderItemRegisterForm.save() requires order=...")

        product = self.cleaned_data["product"]
        product_color = self.cleaned_data["product_color"]
        product_size = self.cleaned_data.get("product_size")

        order_item = super().save(commit=False)
        order_item.order = order
        order_item.product = product
        order_item.image = product_color.image
        order_item.color = product_color.color
        order_item.size = product_size.size if product_size else ""
        order_item.purchase_price = product.purchase_price
        order_item.selling_price = product.get_price()

        if commit:
            order_item.save()
        return order_item


class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status", "free_delivery", "customer_name", "customer_phone", "customer_location", "note"]
        
    def clean_customer_phone(self):
        return validate_phone_number(self.cleaned_data["customer_phone"])
    
    def clean_customer_name(self):
        customer_name = self.cleaned_data["customer_name"].strip()

        if customer_name.isdigit():
            raise ValidationError("اسم المستلم لا يجب أن يكون رقماً فقط.")

        if len(customer_name) < 4:
            raise ValidationError("اسم المستلم يجب أن يكون 4 أحرف أو أكثر.")

        return customer_name
    
    def clean_customer_location(self):
        customer_location = self.cleaned_data["customer_location"].strip()

        if customer_location.isdigit():
            raise ValidationError("العنوان لا يجب أن يكون رقماً فقط.")

        if len(customer_location) < 4:
            raise ValidationError("العنوان  يجب أن يكون 4 أحرف أو أكثر.")

        return customer_location
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["note"].required = False
    

        
