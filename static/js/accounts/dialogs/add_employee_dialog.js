document.addEventListener("DOMContentLoaded", () => {
    const feedback = document.getElementById("username-feedback");
    const add_form = document.getElementById("add_employee_form");
    const usernameInput = document.getElementById("username");
    const checkUsernameUrl = add_form.dataset.checkUrl;
    const dialog = document.getElementById("add_employee_dialog");
    const errorsDiv = document.getElementById("errors");
    let timeout = null;
    let isValidUsername = false;
    // التحقق من صلاحية المعرف أثناء الكتابة
    usernameInput.addEventListener("keyup", async function () {
        isValidUsername = await validateUsername(this, feedback, checkUsernameUrl);
    });
    // التعامل مع نتيجة الدالة الخاصة باضافة موظف جديد
    add_form.addEventListener("submit", function(event) {
        event.preventDefault(); 
        const formData = new FormData(add_form);
        const url = add_form.action;

        if (!isValidUsername) {
            event.preventDefault();
            feedback.innerText = "الرجاء اختيار معَرف صالح اولاً .";
            feedback.style.color = "red";
            return;
        }
        fetch(url, {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                dialog.close();
                showToast("success-toast", data.message);
                setTimeout(() => {
                    location.reload();
                }, 500);
            } else {
                let errors = data.message; 
                errorsDiv.innerHTML = ""; 
                let messages = [];
                if (typeof errors === "string") {
                    // حالة رسالة نصية عامة
                    messages.push(errors);
                } else {
                    // حالة أخطاء الفورم (object)
                    for (let field in errors) {
                        errors[field].forEach(msg => {
                            messages.push(msg);
                        });
                    }
                }
                
                errorsDiv.innerText = messages.join("\n");
                errorsDiv.style.display = "block";
            }
        })
        .catch(error => {
            errorsDiv.innerText = "حدث خطأ غير متوقع.";
        });            
    });
});