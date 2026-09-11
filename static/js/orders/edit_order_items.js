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

function updateTableRows(item) {
    
}