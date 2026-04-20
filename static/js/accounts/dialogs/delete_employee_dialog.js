function openDeleteDialog(button) {
    // جيب قيمة الاسم والاي دي من الداتا سيت
    const employeeId = button.dataset.id;
    const employeeName = button.dataset.name;
    document.getElementById("delete-employee-id").value = employeeId;    // خزّن الاي دي في الحقل المخفي
    document.getElementById("delete-employee-name").innerText = employeeName;   // اعرض الاسم في النص
    delete_employee_dialog.showModal();
}
document.addEventListener("DOMContentLoaded", () => {
    // التعامل مع نتيجة الدالة الخاصة بحذف موظف
    const deleteForm = document.getElementById("delete_employee_form");
    const deleteDialog = document.getElementById("delete_employee_dialog");

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
                setTimeout(() => {
                    location.reload();
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