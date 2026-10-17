// (تعمل  مع ملف cart.js)
// عرض السلة في صفحة إنشاء الطلب اليدوي.
function renderCart() {
    // الحصول على عناصر واجهة السلة.
    const cartItems = document.getElementById("cart-items");
    const template = document.getElementById("cart-item-template");
    const cartForm = document.getElementById("cart_form");

    if (!cartItems || !template || !cartForm) return;

    // إعادة بناء البطاقات وفق بيانات السلة الحالية.
    cartItems.replaceChildren();

    cartProducts.forEach((item, index) => {
        // إنشاء بطاقة جديدة من القالب.
        const fragment = template.content.cloneNode(true);

        const cartItem = fragment.querySelector(".cart-item");
        const image = fragment.querySelector(".item-image");
        const name = fragment.querySelector(".item-name");
        const color = fragment.querySelector(".item-color");
        const size = fragment.querySelector(".item-size");
        const quantity = fragment.querySelector(".item-qty");
        const price = fragment.querySelector(".item-price-value");
        const total = fragment.querySelector(".item-total-value");
        const removeButton = fragment.querySelector(".remove");

        // تعبئة بيانات المنتج.
        cartItem.dataset.cartIndex = index;

        image.src = item.product_image;
        image.alt = item.product_name;

        name.textContent = item.product_name;
        color.textContent = item.color_name;
        size.textContent = item.size_name;

        quantity.textContent = item.qty;
        price.textContent = item.product_price;
        total.textContent = item.product_price * item.qty;

        // ربط زر الحذف بالعنصر.
        removeButton.onclick = () => removeCartItem(index);

        // إضافة البطاقة إلى السلة.
        cartItems.appendChild(fragment);
    });

    // تحديث إجماليات السلة.
    const summary = getCartSummary();

    const cartCount = document.getElementById("cart-count");

    if (cartCount) {
        cartCount.textContent = `(${cartProducts.length})`;
    }

    document.querySelectorAll(".cart-total-qty").forEach(element => {
        element.textContent = summary.totalQuantity;
    });

    document.querySelectorAll(".cart-total-price").forEach(element => {
        element.innerHTML =
            `${summary.totalPrice}<span class="currency">د.ل</span>`;
    });

    // إظهار نموذج السلة عند وجود منتجات.
    cartForm.hidden = cartProducts.length === 0;
}
// إرسال الطلب عند تقديم النموذج.
document.getElementById("cart_form")?.addEventListener("submit", event => {
    event.preventDefault();
    submitOrder(event.currentTarget);
});