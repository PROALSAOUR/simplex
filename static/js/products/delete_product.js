function openDeleteProductDialog(button) {
    // جيب قيمة الاسم والاي دي من الداتا سيت
    const productId = button.dataset.id;
    const productName = button.dataset.name;
    const redirectUrl = button.dataset.redirect;
    document.getElementById("delete-product-id").value = productId;    // خزّن الاي دي في الحقل المخفي
    document.getElementById("delete-product-name").innerText = productName;   // اعرض الاسم في النص
    document.getElementById("delete_product_form").dataset.redirect = redirectUrl; // خزّن الرابط داخل الفورم نفسه عشان نستعمله بعد الحذف
    delete_product_dialog.showModal();
}
document.addEventListener("DOMContentLoaded", () => {
    // التعامل مع نتيجة الدالة الخاصة بحذف موظف
    const deleteForm = document.getElementById("delete_product_form");
    const deleteDialog = document.getElementById("delete_product_dialog");

    deleteForm.addEventListener("submit", function(event) {
        event.preventDefault(); 
        const formData = new FormData(deleteForm);
        const url = deleteForm.action;

        fetch(url, {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                deleteDialog.close();
                showToast("success-toast", data.message);
                // استخدم الرابط المخزن في الفورم  
                const redirectUrl = deleteForm.dataset.redirect;
                setTimeout(() => {
                    window.location.href = redirectUrl;
                }, 500);
            } else {
                deleteDialog.close();
                showToast("failed-toast", data.message);
            }
        })
        .catch(error => {
            deleteDialog.close();
            showToast("failed-toast", "حدث خطأ غير متوقع.");
        });      
    });
});