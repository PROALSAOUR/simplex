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
                    selling: data.order_totals.selling,
                    profit: data.order_totals.profit,
                    purchase: data.order_totals.purchase
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

document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("product-search");
    const searchUrl = searchInput.dataset.searchUrl;
    const resultsContainer = document.getElementById("search-results");
    let searchTimer;
    searchInput.addEventListener("input", function(){
        const query = this.value.trim();
        clearTimeout(searchTimer);
        // إذا كان فارغاً أخفِ النتائج
        if(query.length < 2){
            resultsContainer.innerHTML = "";
            return;
        }
        // انتظار 300ms بعد توقف الكتابة
        searchTimer = setTimeout(() => {
            searchProducts(query);
        }, 300);

    });

    async function searchProducts(query){

        try {

            const response = await fetch(
                `${searchUrl}?q=${encodeURIComponent(query)}`
            );

            const data = await response.json();
            resultsContainer.innerHTML = "";

            if(data.products.length === 0){

                resultsContainer.innerHTML =
                "<p>لا توجد منتجات مطابقة</p>";
                return;
            }

            data.products.forEach(product => {
                resultsContainer.innerHTML += `

                <div class="search-product-card" data-id="${product.id}">
                    <img src="${product.image}" width="70">
                    <span>
                        ${product.name}
                    </span>
                </div>
                `;
            });



        } catch(error){
            console.error(error);
        }
    }
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

function updateTableRows(item) {
    const table  = document.getElementById("item-table");
    const tbody  = table.tBodies[0];
    const productUrlTemplate = table.dataset.productUrlTemplate;
    const  productUrl = productUrlTemplate.replace("0", item.product_id);

    const row = document.createElement("tr");
    row.id = `item-row-${item.id}`;
    row.style.border = "1px solid #ccc";

    row.innerHTML = `
        <td style="padding:10px; border:1px solid #ccc; text-align:center;">
            <img src="${item.image}" alt="${item.product}" style="max-width:100px; height:auto;">
        </td>

        <td style="padding:10px; border:1px solid #ccc;">${item.product}</td>

        <td style="padding:10px; border:1px solid #ccc;">${item.color}</td>

        <td style="padding:10px; border:1px solid #ccc;">${item.size || ""}</td>

        <td class="item-qty"
            data-value="${item.qty}"
            style="padding:10px; border:1px solid #ccc;">
            ${item.qty}
        </td>

        <td style="padding:10px; border:1px solid #ccc;">
            $${item.price}
        </td>

        <td class="item-total"
            data-value="${item.total}"
            style="padding:10px; border:1px solid #ccc;">
            $${item.total}
        </td>

        <td style="padding:10px; border:1px solid #ccc;">
            <button
                type="button"
                class="delete-item-btn"
                data-item-id="${item.id}"
                data-product-name="${item.product}"
                data-color="${item.color}"
                data-size="${item.size}">
                حذف
            </button>

            <a href="${productUrl}" class="btn btn-primary">
                عرض المنتج
            </a>
        </td>
    `;

    tbody.insertBefore(row, tbody.firstElementChild);

}