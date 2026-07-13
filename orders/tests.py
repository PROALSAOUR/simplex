import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Store, UserProfile
from orders.models import Order, OrderItem
from store.models import Product, ProductColor


class AddOrderItemViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vendor", password="secret123")
        self.store = Store.objects.create(
            owner=self.user,
            name="متجر الاختبار",
            status="active",
            phone_number1="0912345678",
        )
        UserProfile.objects.create(user=self.user, user_type="vendor", name="البائع")

        self.product = Product.objects.create(
            store=self.store,
            name="منتج اختبار",
            thumbnail_img="default/default_store_logo.png",
            description="وصف",
            purchase_price=100,
            price=150,
            is_visible=True,
            status="approved",
        )
        self.color = ProductColor.objects.create(product=self.product, color="أحمر", available=True)
        self.order = Order.objects.create(
            store=self.store,
            customer_name="أحمد",
            customer_phone="0912345678",
            customer_location="بنغازي",
        )
        self.order.items.create(
            product=self.product,
            image="default/default_store_logo.png",
            color=self.color.color,
            size="",
            qty=1,
            purchase_price=100,
            selling_price=150,
        )

    def test_add_order_item_returns_success_and_updates_totals(self):
        self.client.force_login(self.user)
        url = reverse("orders:add_order_item", args=[self.order.id])
        payload = {
            "product_id": self.product.id,
            "color_id": self.color.id,
            "qty": 2,
        }

        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(OrderItem.objects.filter(order=self.order).count(), 2)
        self.assertEqual(data["order_total_selling_price"], 450)
        self.assertEqual(data["order_total_purchase_price"], 300)
