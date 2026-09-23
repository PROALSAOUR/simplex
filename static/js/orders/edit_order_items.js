// اكواد و دوال حذف عنصر من الطلب 
function openDeleteItemDialog(button) {
    // جيب قيمة الاسم والاي دي من الداتا سيت
    const itemId = button.dataset.id;
    const productName = button.dataset.name;
    const redirectUrl = button.dataset.redirect;
    document.getElementById("delete-order-item-id").value = itemId;    // خزّن الاي دي في الحقل المخفي
    document.getElementById("delete-order-item-name").innerText = productName;   // اعرض الاسم في النص
    document.getElementById("delete_order_items_form").dataset.redirect = redirectUrl; // خزّن الرابط داخل الفورم نفسه عشان نستعمله بعد الحذف
    delete_order_item_dialog.showModal();
}
function setupDeleteOrderItem() {
    const form = document.getElementById("delete_order_items_form");
    const dialog = document.getElementById("delete_order_item_dialog");

    if (!form || !dialog) {
        return;
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const itemIdInput = document.getElementById("delete-order-item-id");

        if (!itemIdInput || !itemIdInput.value) {
            return;
        }

        const itemId = itemIdInput.value;
        const urlTemplate = form.dataset.url;

        if (!urlTemplate) {
            return;
        }

        // استبدال 0 الموجود في الرابط بالـ ID الحقيقي للعنصر
        const url = urlTemplate.replace("/0/", `/${itemId}/`);

        const csrfToken = form.querySelector(
            "[name='csrfmiddlewaretoken']"
        );

        if (!csrfToken) {
            return;
        }

        fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken.value,
                "X-Requested-With": "XMLHttpRequest",
            },
        })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("حدث خطأ أثناء تنفيذ الطلب.");
            }

            return response.json();
        })
        .then(function (data) {

            if (!data.success) {
                showToast("failed-toast", data.message);
                return;
            }

            // إغلاق نافذة التأكيد
            dialog.close();

            // حذف صف المنتج من الجدول
            const itemRow = document.getElementById(`item-row-${itemId}`);

            if (itemRow) {
                itemRow.remove();
            }

            // تحديث إجماليات الطلب
            updateOrderTotals(data.order_totals);
            updateTableTotals();

            // إظهار رسالة النجاح
            showToast("success-toast", data.message);
        })
        .catch(function (error) {
            console.error(error);
            showToast(
                "failed-toast",
                "حدث خطأ أثناء إزالة المنتج، يرجى المحاولة مرة أخرى."
            );
        });
    });
}

setupDeleteOrderItem();
// =======================================================================================================
// أكواد ودوال إضافة عنصر إلى الطلب

function addOrderItem(button) {
    // إضافة المنتج المحدد إلى الطلب وإظهار أخطاء النموذج داخل البطاقة

    const card = button.closest(".product-card");

    if (!card) {
        return;
    }

    const form = document.getElementById("add_order_items_form");

    if (!form) {
        return;
    }

    const url = form.dataset.url;

    if (!url) {
        return;
    }

    const csrfToken = form.querySelector(
        "[name='csrfmiddlewaretoken']"
    );

    if (!csrfToken) {
        return;
    }

    const productInput = card.querySelector(
        "input[name^='product_']"
    );

    const colorInput = card.querySelector(
        "input[name^='color_']:checked"
    );

    const quantityInput = card.querySelector(
        ".qty-input"
    );

    const errorsContainer = card.querySelector(".field-errors");

    // إخفاء الأخطاء السابقة
    if (errorsContainer) {
        errorsContainer.textContent = "";
        errorsContainer.classList.add("hidden");
    }

    if (!productInput || !colorInput || !quantityInput) {
        showToast(
            "failed-toast",
            "يرجى اختيار بيانات المنتج."
        );
        return;
    }

    const colorId = colorInput.value;

    const sizeGroup = card.querySelector(
        `.size-group[data-color-id="${colorId}"]`
    );

    const sizeInput = sizeGroup
        ? sizeGroup.querySelector("input[type='radio']:checked")
        : null;

    const sizeId = sizeInput && !sizeInput.dataset.unifiedSize
    ? sizeInput.value
    : "";

    const formData = new FormData();

    formData.append(
        "csrfmiddlewaretoken",
        csrfToken.value
    );

    formData.append(
        "product_id",
        productInput.value
    );

    formData.append(
        "color_id",
        colorId
    );

    formData.append(
        "size_id",
        sizeId
    );

    formData.append(
        "quantity",
        quantityInput.value
    );

    fetch(url, {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
    })
    .then(function (response) {
        if (!response.ok) {
            throw new Error(
                "حدث خطأ أثناء تنفيذ الطلب."
            );
        }

        return response.json();
    })
    .then(function (data) {

        if (!data.success) {

            // عرض الأخطاء داخل بطاقة المنتج
            if (errorsContainer && data.errors) {

                const errorMessages = [];

                Object.values(data.errors).forEach(function (errors) {
                    errors.forEach(function (error) {
                        errorMessages.push(error);
                    });
                });

                if (errorMessages.length) {
                    errorsContainer.innerHTML = errorMessages
                        .map(error => `<div>${error}</div>`)
                        .join("");

                    errorsContainer.classList.remove("hidden");
                }
            }

            showToast(
                "failed-toast",
                data.message
            );

            return;
        }

        // إضافة الصف الجديد إلى جدول المنتجات
        appendTableRow(data.item_html);

        // تحديث إجماليات الطلب
        updateOrderTotals(data.order_totals);

        // تحديث إجمالي الكمية والسعر داخل الجدول
        updateTableTotals();

        // اغلاق بانل إضافة منتج
        closeAddItemPanel();

        // إظهار رسالة النجاح
        showToast(
            "success-toast",
            data.message
        );

        // إغلاق بطاقة المنتج بعد إضافته
        card.open = false;

        // إعادة الكمية إلى القيمة الافتراضية
        quantityInput.value = 1;
    })
    .catch(function (error) {
        console.error(error);

        showToast(
            "failed-toast",
            "حدث خطأ أثناء إضافة المنتج، يرجى المحاولة مرة أخرى."
        );
    });
}

function appendTableRow(itemHtml) {
    // إضافة صف جديد إلى نهاية جدول الطلب
    const tbody = document.querySelector("#item-table tbody");

    if (!tbody) {
        return;
    }

    tbody.insertAdjacentHTML("beforeend", itemHtml);
}

function closeAddItemPanel() {
    // إغلاق بانل إضافة المنتج بعد إتمام الإضافة
    const panel = document.querySelector(".add-item-panel");

    if (!panel) {
        return;
    }

    panel.classList.remove("open");
}
// =======================================================================================================
//  اكواد و دوال مشتركة بين الاضافة والحذف 
function updateTableTotals() {
    // دالة لتحديث إجمالي الكمية والسعر الإجمالي للمنتجات في الطلب داخل الجدول
    // يتم استدعائها بمجرد تحميل الصفحة وايضا عند حذف او اضافة أي منتج من الطلب لتحديث القيم المعروضة
    let totalQty = 0;
    let totalPrice = 0;

    document.querySelectorAll("#item-table tbody tr").forEach(row => {
        const qtyElement = row.querySelector(".item-qty");
        const priceElement = row.querySelector(".item-total");

        if (!qtyElement || !priceElement) {
            return;
        }

        const qty = Number(qtyElement.dataset.value) || 0;
        const price = Number(priceElement.dataset.value) || 0;

        totalQty += qty;
        totalPrice += price;
    });

    const totalQtyElement = document.getElementById("total-qty");
    if (totalQtyElement) {
        totalQtyElement.textContent = totalQty;
    }

    const totalPriceElement = document.getElementById("total-price");
    if (totalPriceElement) {        
        totalPriceElement.textContent = totalPrice;
    }
}

function updateOrderTotals(totals) {
    // دالة لتحديث إجمالي سعر شراء المنتجات، إجمالي سعر بيع المنتجات، وإجمالي الربح للطلب
    // يتم استدعائها عند حذف او اضافة أي منتج من الطلب لتحديث القيم المعروضة
    // يجب تمرير قيم اليها عند استدعائها

    const purchaseElement = document.getElementById("total_purchase_price");
    if (purchaseElement) {
        purchaseElement.textContent = ` ${totals.purchase} `;
    }

    // تحديث إجمالي سعر بيع المنتجات
    const sellingElement = document.getElementById("total_selling_price");
    if (sellingElement) {
        sellingElement.textContent = ` ${totals.selling} `;
    }

    // تحديث إجمالي الربح
    const profitElement = document.getElementById("total_profit");
    if (profitElement) {
        profitElement.textContent = ` ${totals.profit} `;
    }
}
// =======================================================================================================
// في مربع نتائج البحث منع فتح اكثر من بطاقة منتج واحدة لمنع الزحام 
function setupProductCards() {
    // السماح بفتح بطاقة منتج واحدة فقط حتى مع إضافة البطاقات ديناميكيًا
    const container = document.querySelector("#search-results");

    if (!container) return;

    function setupCard(card) {
        card.addEventListener("toggle", () => {
            if (!card.open) return;

            container.querySelectorAll("details.product-card").forEach(otherCard => {
                if (otherCard !== card && otherCard.open) {
                    otherCard.open = false;
                }
            });
        });
    }

    // تفعيل البطاقات الموجودة حاليًا
    container.querySelectorAll("details.product-card").forEach(setupCard);

    // تفعيل أي بطاقة تتم إضافتها لاحقًا
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType !== Node.ELEMENT_NODE) return;

                if (node.matches("details.product-card")) {
                    setupCard(node);
                }

                node.querySelectorAll?.("details.product-card").forEach(setupCard);
            });
        });
    });

    observer.observe(container, {
        childList: true,
        subtree: true
    });
}
setupProductCards();
// =======================================================================================================
