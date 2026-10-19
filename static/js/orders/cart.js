// تعمل مع كل من ملفات view-product.js و add_order_manually.js

// قائمة السلة: نحتفظ ببيانات المنتجات والاختيارات والكميات.
const cartProducts = [];

// إضافة المنتج المحدد إلى السلة.
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

    const quantityInput = productCard.querySelector(".qty-input");
    const quantity = Number(quantityInput?.value) || 1;

    // الحصول على بيانات المنتج.
    const productName = productCard.dataset.productName || "";
    const productPrice = parseFloat(
        productCard.dataset.productPrice
    ) || 0;

    // البحث عن العنصر نفسه بالمنتج واللون والمقاس.
    const existingItem = cartProducts.find(item =>
        item.product_id === productId &&
        item.color_id === colorId &&
        item.size_id === sizeId
    );

    if (existingItem) {
        // زيادة كمية العنصر الموجود.
        existingItem.qty += quantity;
    } else {
        // إضافة عنصر جديد إلى السلة.
        cartProducts.push({
            product_id: productId,
            product_name: productName,
            product_price: productPrice,
            product_image:
                colorInput?.dataset.colorImage ||
                productCard.querySelector("img")?.src ||
                "/images/deafult.jpg",
            color_id: colorId,
            color_name: colorInput?.dataset.colorName || "",
            size_id: sizeId,
            size_name: sizeInput?.dataset.sizeName || "مقاس موحد",
            qty: quantity
        });
    }

    // تحديث واجهة السلة الخاصة بالصفحة الحالية.
    renderCart();
}

// حساب إجماليات السلة.
function getCartSummary() {
    // حساب إجمالي الكمية والسعر.
    return cartProducts.reduce(
        (summary, item) => {
            summary.totalQuantity += item.qty;
            summary.totalPrice += item.product_price * item.qty;

            return summary;
        },
        {
            totalQuantity: 0,
            totalPrice: 0
        }
    );
}

// حذف عنصر من السلة.
function removeCartItem(index) {
    // حذف العنصر من بيانات السلة.
    if (index < 0 || index >= cartProducts.length) return;

    cartProducts.splice(index, 1);

    // تحديث واجهة السلة.
    renderCart();
}

// تحديث كمية عنصر في السلة.
function updateCartItemQuantity(index, quantity) {
    // التحقق من الفهرس والكمية.
    if (
        index < 0 ||
        index >= cartProducts.length ||
        !Number.isInteger(quantity) ||
        quantity < 1
    ) {
        return;
    }

    cartProducts[index].qty = quantity;

    // تحديث واجهة السلة.
    renderCart();
}

// عرض أخطاء بيانات الزبون وأخطاء منتجات الطلب.
function displayFormErrors(form, errors = {}, itemErrors = {}) {
    const customerErrors = form.querySelector("#customer-errors");
    const itemsErrors = form.querySelector("#items-errors");

    // مسح الأخطاء السابقة.
    customerErrors?.replaceChildren();
    itemsErrors?.replaceChildren();

    // عرض أخطاء بيانات الزبون.
    if (customerErrors) {
        Object.values(errors).flat().forEach(message => {
            const error = document.createElement("div");
            error.textContent = message;
            customerErrors.appendChild(error);
        });
        customerErrors.hidden = !customerErrors.children.length;
    }

    // عرض أخطاء المنتجات.
    if (itemsErrors) {
        const messages = [];

        Object.entries(itemErrors).forEach(([index, item]) => {
            if (index === "__all__") {
                messages.push(...(Array.isArray(item) ? item : []));
                return;
            }

            if (item && typeof item === "object") {
                Object.values(item).forEach(fieldErrors => {
                    if (Array.isArray(fieldErrors)) {
                        messages.push(...fieldErrors);
                    }
                });
            }
        });

        [...new Set(messages)].forEach(message => {
            const error = document.createElement("div");
            error.textContent = message;
            itemsErrors.appendChild(error);
        });
        itemsErrors.hidden = !itemsErrors.children.length;
    }
}

function showThankYouModal() {
    const thanksModal = document.getElementById("thanks-modal");
    if (!thanksModal ) return;
        thanksModal.classList.add("show");
        window.setTimeout(() => {
            thanksModal.classList.remove("show");
        }, 2500);
}
// ===========================================================================
// كود التحقق من صحة رقم الهاتف بشكل مباشر اثناء الكتابة
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("cart_form");
    const phoneInput = document.getElementById("id_customer_phone");
    const feedback = document.getElementById("phone-feedback");

    if (!form || !phoneInput || !feedback) return;

    const checkPhoneUrl = form.dataset.checkUrl;

    let isValidPhonenumber = false;

    // التحقق عند تغيير قيمة رقم الهاتف.
    phoneInput.addEventListener("input", async function () {
        isValidPhonenumber = false;

        isValidPhonenumber = await validatePhoneNumber(
            this,
            feedback,
            checkPhoneUrl
        );
    });

    // منع إرسال الطلب إذا كان رقم الهاتف غير صالح.
    form.addEventListener("submit", function (event) {
        if (!isValidPhonenumber) {
            event.preventDefault();

            feedback.innerText = "يرجى إدخال رقم هاتف صالح.";
            feedback.style.color = "red";

            phoneInput.focus();
        }
    });
});
// ============================================================================
//  إرسال بيانات الطلب إلى الخادم وعرض نتيجة العملية.
async function submitOrder(form) {
    const url = form.dataset.submitUrl;

    const csrfToken = form.querySelector(
        '[name="csrfmiddlewaretoken"]'
    ).value;

    const formData = new FormData(form);

    const data = {
        ...Object.fromEntries(formData.entries()),
        free_delivery: formData.has("free_delivery"),
        items: cartProducts.map(item => ({
            product_id: item.product_id,
            color_id: item.color_id,
            size_id: item.size_id,
            qty: item.qty
        }))
    };

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            displayFormErrors(
                form,
                result.errors || {},
                result.item_errors || {}
            );
            return;
        }

        // اظهار الشكرية الناجحة.
        
        showThankYouModal();

        form.reset();
        cartProducts.length = 0;
        renderCart();
        setTimeout(() => {
            window.location.href = form.dataset.redirectUrl;
        }, 3000);

    } catch (error) {
        console.error("Submit order error:", error);
    }
}

