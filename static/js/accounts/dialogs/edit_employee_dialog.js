function openEditDialog(button) {
    // جيب قيمة الاسم والاي دي من الداتا سيت
    const employeeId = button.dataset.id;
    const employeeName = button.dataset.name;
    document.getElementById("edit-employee-id").value = employeeId;    // خزّن الاي دي في الحقل المخفي
    document.getElementById("edit-employee-name").innerText = employeeName;   // اعرض الاسم في النص
    edit_employee_dialog.showModal();
}
document.addEventListener("DOMContentLoaded", () => {
    // التعامل مع نتيجة الدالة الخاصة بحذف موظف
    const editForm = document.getElementById("edit_employee_form");
    const editDialog = document.getElementById("edit_employee_dialog");

    editForm.addEventListener("submit", function(event) {
        event.preventDefault(); 
        const formData = new FormData(editForm);
        const url = editForm.action;

        fetch(url, {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                editDialog.close();
                showToast("success-toast", data.message);
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                editDialog.close();
                showToast("failed-toast", data.message);
            }
        })
        .catch(error => {
            editDialog.close();
            showToast("failed-toast", "حدث خطأ غير متوقع.");
        });      
    });
});