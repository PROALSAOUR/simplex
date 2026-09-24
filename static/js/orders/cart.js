// قائمة السلة: نحتفظ بالمعرفات والاختيارات والكميات فقط.
const cartProducts = [];


/**
 * إضافة المنتج المحدد إلى السلة.
 */
function addToCart(button) {
    // الحصول على بطاقة المنتج والاختيارات المحددة.
    const productCard = button.closest(".product-card");
    if (!productCard) return;

    const productId = productCard.dataset.productId;

    const colorInput = productCard.querySelector(
        'input[name^="color_"]:checked'
    );

    const colorId = colorInput?.value || null;

    const sizeGroup = colorId
        ? productCard.querySelector(
            `.size-group[data-color-id="${colorId}"]`
        )
        : null;

    const sizeInput = sizeGroup?.querySelector(
        'input[type="radio"]:checked'
    );

    // المقاس الموحد لا يملك معرفًا.
    const sizeId =
        sizeInput?.dataset.unifiedSize === "true"
            ? null
            : (sizeInput?.value || null);

    const quantityInput =
        productCard.querySelector(".qty-input");

    const quantity =
        Number(quantityInput?.value) || 1;

    // البحث عن نفس المنتج بنفس اللون والمقاس.
    const existingIndex = cartProducts.findIndex(item =>
        item.product_id === productId &&
        item.color_id === colorId &&
        item.size_id === sizeId
    );

    if (existingIndex !== -1) {
        // زيادة كمية العنصر الموجود بدل إنشاء بطاقة جديدة.
        cartProducts[existingIndex].qty += quantity;

        updateCartItem(
            existingIndex,
            cartProducts[existingIndex].qty
        );

        updateCartSummary();

        return;
    }

    // إضافة عنصر جديد إلى السلة.
    cartProducts.push({
        product_id: productId,
        color_id: colorId,
        size_id: sizeId,
        qty: quantity
    });

    // إضافة بطاقة جديدة للمنتج.
    appendCartItem(
        productCard,
        cartProducts.length - 1
    );

    updateCartSummary();
}


/**
 * إضافة بطاقة جديدة إلى السلة.
 */
function appendCartItem(productCard, index) {
    // الحصول على عناصر السلة والقالب.
    const cartItems =
        document.getElementById("cart-items");

    const template =
        document.getElementById("cart-item-template");

    const cartForm =
        document.getElementById("cart_form");

    if (!cartItems || !template || !cartForm) return;

    const item =
        cartProducts[index];

    // بيانات المنتج للعرض فقط.
    const productName =
        productCard.dataset.productName || "";

    const productPrice =
        parseFloat(
            productCard.dataset.productPrice
        ) || 0;

    const productImage =
        productCard.querySelector("img")?.src ||
        "/images/deafult.jpg";

    // بيانات اللون.
    const colorInput = item.color_id
        ? productCard.querySelector(
            `input[name="color_${item.product_id}"][value="${item.color_id}"]`
        )
        : null;

    const colorName =
        colorInput?.dataset.colorName || "";

    const colorImage =
        colorInput?.dataset.colorImage || "";

    // بيانات المقاس.
    let sizeName = "مقاس موحد";

    if (item.size_id) {
        const sizeInput =
            productCard.querySelector(
                `input[value="${item.size_id}"]`
            );

        sizeName =
            sizeInput?.dataset.sizeName ||
            "مقاس موحد";
    }

    // إنشاء نسخة مستقلة من قالب عنصر السلة.
    const cartItem =
        template.content.cloneNode(true);

    const cartItemElement =
        cartItem.querySelector(".cart-item");

    const image =
        cartItem.querySelector(".item-image");

    const name =
        cartItem.querySelector(".item-name");

    const color =
        cartItem.querySelector(".item-color");

    const size =
        cartItem.querySelector(".item-size");

    const quantity =
        cartItem.querySelector(".item-qty");

    const price =
        cartItem.querySelector(".item-price-value");

    const total =
        cartItem.querySelector(".item-total-value");

    const removeButton =
        cartItem.querySelector(".remove");

    // ربط بطاقة العرض بموقع العنصر في السلة.
    cartItemElement.dataset.cartIndex = index;

    // تعبئة بيانات العرض.
    image.src =
        colorImage || productImage;

    name.textContent =
        productName;

    color.textContent =
        colorName;

    size.textContent =
        sizeName;

    quantity.textContent =
        item.qty;

    price.textContent =
        productPrice;

    // حساب إجمالي هذا العنصر.
    total.textContent =
        productPrice * item.qty;

    // زر حذف العنصر.
    removeButton.onclick = () => {
        removeFromCart(index, cartItemElement);
    };

    // إضافة البطاقة الجديدة دون حذف البطاقات السابقة.
    cartItems.appendChild(cartItem);

    // إظهار السلة.
    cartForm.hidden = false;
}

/**
 * تحديث كمية بطاقة موجودة في السلة.
 */
function updateCartItem(index, quantity) {
    // البحث عن بطاقة العنصر وتحديث كمية وإجمالي المنتج.
    const cartItem =
        document.querySelector(
            `.cart-item[data-cart-index="${index}"]`
        );

    if (!cartItem) return;

    const quantityElement =
        cartItem.querySelector(".item-qty");

    const totalElement =
        cartItem.querySelector(".item-total-value");

    if (quantityElement) {
        quantityElement.textContent = quantity;
    }

    const priceElement =
        cartItem.querySelector(".item-price-value");

    const price =
        parseFloat(priceElement?.textContent) || 0;

    if (totalElement) {
        totalElement.textContent =
            price * quantity;
    }
}


/**
 * تحديث إجماليات السلة.
 */
function updateCartSummary() {
    // حساب إجمالي الكمية والسعر.
    let totalQuantity = 0;
    let totalPrice = 0;

    cartProducts.forEach(item => {
        const productCard =
            document.querySelector(
                `.product-card[data-product-id="${item.product_id}"]`
            );

        // إذا لم تعد بطاقة المنتج موجودة، لا نستخدمها للحساب.
        if (!productCard) return;

        const productPrice =
            parseFloat(
                productCard.dataset.productPrice
            ) || 0;

        totalQuantity += item.qty;
        totalPrice += productPrice * item.qty;
    });

    // تحديث عدد عناصر السلة.
    const cartCount =
        document.getElementById("cart-count");

    if (cartCount) {
        cartCount.textContent =
            `(${cartProducts.length})`;
    }

    // تحديث إجمالي الكمية.
    const cartTotalQty =
        document.getElementById("cart-total-qty");

    if (cartTotalQty) {
        cartTotalQty.textContent =
            totalQuantity;
    }

    // تحديث إجمالي السعر.
    const cartTotalPrice =
        document.getElementById("cart-total-price");

    if (cartTotalPrice) {
        cartTotalPrice.innerHTML =
            `${totalPrice}<span class="currency">د.ل</span>`;
    }

    // إظهار أو إخفاء السلة.
    const cartForm =
        document.getElementById("cart_form");

    if (cartForm) {
        cartForm.hidden =
            cartProducts.length === 0;
    }
}


/**
 * حذف منتج من السلة.
 */
function removeFromCart(index, cartItemElement) {
    // حذف العنصر من القائمة ومن واجهة السلة.
    cartProducts.splice(index, 1);

    cartItemElement.remove();

    // تحديث الفهارس بعد الحذف.
    document
        .querySelectorAll("#cart-items .cart-item")
        .forEach((item, newIndex) => {
            item.dataset.cartIndex = newIndex;

            const removeButton =
                item.querySelector(".remove");

            removeButton.onclick = () => {
                removeFromCart(
                    newIndex,
                    item
                );
            };
        });

    // تحديث إجماليات السلة.
    updateCartSummary();
}