document.addEventListener("DOMContentLoaded", () => {
    updateTableTotals();
    const delete_dialog = document.getElementById("delete_order_items");
    const delete_form = document.getElementById("delete_order_items_form");
    const delete_message = document.getElementById("delete_item_message");


    const add_dialog = document.getElementById("add_order_items");

    

    // الاكواد التاليه للتعامل مع حذف المنتجات من الطلب

    document.addEventListener("click", function (e) {

        const button = e.target.closest(".delete-item-btn");
        if (!button) return;

        const itemId = button.dataset.itemId;

        let productName = `${button.dataset.productName} - ${button.dataset.color}`;

        if (button.dataset.size) {
            productName += ` - ${button.dataset.size}`;
        }

        delete_form.dataset.itemId = itemId;

        delete_message.textContent =
            `هل أنت متأكد من حذف المنتج "${productName}" من الطلب؟`;

        delete_dialog.showModal();

    });

    delete_form.addEventListener("submit", async function (e) {

        e.preventDefault();

        const itemId = this.dataset.itemId;
        const url = this.dataset.url.replace("/0/", `/${itemId}/`);

        const csrf = this.querySelector(
            "input[name=csrfmiddlewaretoken]"
        ).value;

        try {

            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrf,
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const data = await response.json();

            if (data.success) {

                delete_dialog.close();

                // حذف الصف من الجدول
                document.getElementById(`item-row-${itemId}`)?.remove();
                updateTableTotals();
                updateOrderTotals( {
                    selling: data.order_total_selling_price,
                    profit: data.order_total_profit,
                    purchase: data.order_total_purchase_price
                });
                showToast("success-toast", "تم حذف المنتج من الطلب بنجاح");

            } else {
                showToast("failed-toast", data.message);
            }

        } catch (error) {

            console.error(error);
            showToast("failed-toast", "حدث خطأ غير متوقع.");

        }

    });

});

function updateTableTotals() {
    // دالة لتحديث إجمالي الكمية والسعر الإجمالي للمنتجات في الطلب داخل الجدول
    // يتم استدعائها بمجرد تحميل الصفحة وايضا عند حذف او اضافة أي منتج من الطلب لتحديث القيم المعروضة
    let totalQty = 0;
    let totalPrice = 0;

    document.querySelectorAll("#item-table tbody tr").forEach(row => {

        if (row.id === "totals-row")
            return;

        const qty = Number(row.querySelector(".item-qty").dataset.value);
        const price = Number(row.querySelector(".item-total").dataset.value);

        totalQty += qty;
        totalPrice += price;

    });

    document.getElementById("total-qty").textContent = totalQty;
    document.getElementById("total-price").textContent = `$${totalPrice}`;
}

function updateOrderTotals(totals) {
    // دالة لتحديث إجمالي سعر شراء المنتجات، إجمالي سعر بيع المنتجات، وإجمالي الربح للطلب
    // يتم استدعائها عند حذف او اضافة أي منتج من الطلب لتحديث القيم المعروضة
    // يجب تمرير قيم اليها عند استدعائها

    const purchaseElement = document.getElementById("order_total_purchase_price");
    if (purchaseElement) {
        purchaseElement.textContent =  totals.purchase;
    }

    // تحديث إجمالي سعر بيع المنتجات
    const sellingElement = document.getElementById("order_total_selling_price");
    if (sellingElement) {
        sellingElement.textContent =  totals.selling;
    }

    // تحديث إجمالي الربح
    const profitElement = document.getElementById("order_total_profit");
    if (profitElement) {
        profitElement.textContent =  totals.profit;
    }
}