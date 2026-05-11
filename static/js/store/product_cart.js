(function () {
    const form = document.getElementById("product-form");
    const cart = document.getElementById("cart");
    const cartItems = document.getElementById("cart-items");
    const totalQty = document.getElementById("total-qty");
    const totalPrice = document.getElementById("total-price");
    const sizesWrapper = document.getElementById("sizes-wrapper");
    const orderForm = document.getElementById("order-form");
    const orderModal = document.getElementById("order-modal");
    const orderMessage = document.getElementById("order-message");
    const quantityInput = document.getElementById("quantity");
    const qtyMinus = document.getElementById("qty-minus");
    const qtyPlus = document.getElementById("qty-plus");
    const sizeGroups = document.querySelectorAll(".size-group");
    const cartProducts = [];

    if (!form && !orderForm) return;

    const productData = {
        id: form ? form.dataset.productId : "",
        name: form ? form.dataset.productName : "",
        price: form ? Number(form.dataset.productPrice || 0) : 0,
        image: form ? form.dataset.productImage : "",
    };

    function escapeHtml(value) {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function getSelectedColor() {
        return document.querySelector('input[name="color"]:checked');
    }

    function getActiveSize() {
        const color = getSelectedColor();
        if (!color) return null;

        const activeGroup = document.querySelector(`.size-group[data-color-id="${color.value}"]`);
        return activeGroup ? activeGroup.querySelector("input:checked") : null;
    }

    function showSizesForColor(colorId) {
        let hasSizes = false;

        sizeGroups.forEach((group) => {
            const isActive = group.dataset.colorId === colorId;
            group.classList.toggle("active", isActive);

            if (isActive) {
                hasSizes = true;
                const firstSize = group.querySelector("input");
                if (firstSize) firstSize.checked = true;
            }
        });

        if (sizesWrapper) {
            sizesWrapper.classList.toggle("hidden", !hasSizes);
        }
    }

    function renderCart() {
        if (!cart || !cartItems || !totalQty || !totalPrice) return;

        cart.classList.toggle("show", cartProducts.length > 0);

        cartItems.innerHTML = cartProducts.map((item, index) => `
            <div class="cart-item">
                <img src="${escapeHtml(item.image)}" alt="${escapeHtml(item.name)}">
                <div>
                    <h3>${escapeHtml(item.name)}</h3>
                    <p>اللون: ${escapeHtml(item.colorName)}</p>
                    ${item.sizeName ? `<p>المقاس: ${escapeHtml(item.sizeName)}</p>` : ""}
                    <p>السعر: ${item.price.toFixed(2)} د.ل</p>
                    <p>الكمية: ${item.qty}</p>
                </div>
                <button class="remove" type="button" data-index="${index}">حذف</button>
            </div>
        `).join("");

        const qty = cartProducts.reduce((sum, item) => sum + item.qty, 0);
        const price = cartProducts.reduce((sum, item) => sum + (item.price * item.qty), 0);
        totalQty.textContent = qty;
        totalPrice.textContent = price.toFixed(2);
    }

    function clearOrderErrors() {
        document.querySelectorAll(".form-error").forEach((error) => {
            error.textContent = "";
        });
    }

    function showOrderErrors(responseData) {
        clearOrderErrors();

        Object.entries(responseData.errors || {}).forEach(([field, messages]) => {
            const errorElement = document.getElementById(`error-${field}`);
            if (errorElement) {
                errorElement.textContent = messages.join(" ");
            }
        });

        const orderError = document.getElementById("error-order");
        const itemErrors = responseData.item_errors || {};
        const itemMessages = Object.values(itemErrors).flatMap((fieldErrors) => {
            if (Array.isArray(fieldErrors)) return fieldErrors;
            return Object.values(fieldErrors).flat();
        });

        if (orderError) {
            orderError.textContent = itemMessages.length
                ? itemMessages.join(" ")
                : (responseData.message || "");
        }
    }

    function showThankYouModal(message) {
        if (!orderModal || !orderMessage) return;

        orderMessage.textContent = message;
        orderModal.classList.add("show");

        window.setTimeout(() => {
            orderModal.classList.remove("show");
        }, 3500);
    }

    function updateQuantity(change) {
        if (!quantityInput) return;

        const min = Number(quantityInput.min || 1);
        const max = Number(quantityInput.max || min);
        const current = Number(quantityInput.value || min);
        const next = Math.min(max, Math.max(min, current + change));
        quantityInput.value = next;
    }

    document.querySelectorAll('input[name="color"]').forEach((input) => {
        input.addEventListener("change", () => showSizesForColor(input.value));
    });

    if (getSelectedColor()) {
        showSizesForColor(getSelectedColor().value);
    }

    if (qtyMinus) {
        qtyMinus.addEventListener("click", () => updateQuantity(-1));
    }

    if (qtyPlus) {
        qtyPlus.addEventListener("click", () => updateQuantity(1));
    }

    if (quantityInput) {
        quantityInput.addEventListener("change", () => updateQuantity(0));
    }

    if (form) {
        form.addEventListener("submit", (event) => {
            event.preventDefault();

            const color = getSelectedColor();
            const size = getActiveSize();
            const qty = Math.max(1, Number(quantityInput.value || 1));

            if (!color) return;

            cartProducts.push({
                product_id: productData.id,
                name: productData.name,
                price: productData.price,
                image: color.dataset.colorImage || productData.image,
                color_id: color.value,
                colorName: color.dataset.colorName,
                size_id: size ? size.value : "",
                sizeName: size ? size.dataset.sizeName : "",
                qty,
            });

            quantityInput.value = 1;
            renderCart();
        });
    }

    if (orderForm) {
        orderForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            if (!cartProducts.length) return;
            if (!orderForm.checkValidity()) {
                orderForm.reportValidity();
                return;
            }

            clearOrderErrors();

            const csrfToken = orderForm.querySelector("[name=csrfmiddlewaretoken]").value;
            const payload = {
                customer_name: document.getElementById("customer-name").value,
                customer_phone: document.getElementById("customer-phone").value,
                customer_location: document.getElementById("customer-location").value,
                items: cartProducts.map((item) => ({
                    product_id: item.product_id,
                    color_id: item.color_id,
                    size_id: item.size_id,
                    qty: item.qty,
                })),
            };

            try {
                const response = await fetch(orderForm.action, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: JSON.stringify(payload),
                });
                const responseData = await response.json();

                if (responseData.success) {
                    cartProducts.length = 0;
                    renderCart();
                    orderForm.reset();
                    showThankYouModal(responseData.message);
                    return;
                }

                showOrderErrors(responseData);
            } catch (error) {
                showOrderErrors({
                    message: "تعذر إرسال الطلب، يرجى المحاولة مرة أخرى.",
                });
            }
        });
    }

    if (cartItems) {
        cartItems.addEventListener("click", (event) => {
            const button = event.target.closest(".remove");
            if (!button) return;

            cartProducts.splice(Number(button.dataset.index), 1);
            renderCart();
        });
    }
})();
