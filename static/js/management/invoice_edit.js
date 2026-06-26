document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("edit_invoice_form");
    const dialog = document.getElementById("edit_invoice");
    const errorsDiv = document.getElementById("errors");
    const haveDiscount = document.getElementById("have_discount");
    const discountFields = document.getElementById("discount_fields");

    function toggleDiscountFields() {
        if (haveDiscount.checked) {
            discountFields.style.display = "block";
            document.getElementById('discount').disabled = false;
        } else {
            discountFields.style.display = "none";
            document.getElementById('discount').disabled = true;
        }
    }
    // تنفيذها عند تحميل الصفحة
    toggleDiscountFields();
    // تنفيذها عند تغيير حالة الـ checkbox
    haveDiscount.addEventListener("change", toggleDiscountFields);

    // التعامل مع نتيجة الدالة الخاصة بتعديل بيانات الحساب
    form.addEventListener("submit", function(event) {

        event.preventDefault(); 
        const formData = new FormData(form);
        const url = form.action;

        fetch(url, {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                document.getElementById("invoice_status").innerText = data.invoice_status;
                document.getElementById("invoice_notes").innerText = data.notes || "لايوجد ملاحظات بعد";
                document.getElementById("invoice_commission_value").innerText = data.commission_value;
                document.getElementById("invoice_final_value").innerText = data.final_value;
                document.getElementById("invoice_discount").innerText = data.discount;
                dialog.close();
                showToast("success-toast", data.message);
            } else {
                errorsDiv.innerText = data.message;
                errorsDiv.style.display = "block";
            }
        })
        .catch(error => {
            errorsDiv.innerText = "حدث خطأ غير متوقع.";
        });            
    });
});
function updateFinalValue() {
    const commission = parseFloat(
        document.getElementById('commission_value').dataset.value || 0
    );

    let discount = parseFloat(
        document.getElementById('discount').value || 0
    );

    // منع القيم السالبة
    if (discount < 0) {
        discount = 0;
        document.getElementById("discount").value = 0;
    }

    document.getElementById('final_value').innerText =
        Math.max(0, commission - discount).toFixed(2);
}
