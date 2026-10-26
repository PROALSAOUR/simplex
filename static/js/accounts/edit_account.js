// كود التحكم بفورم تغيير بيانات المستخدم
document.addEventListener("DOMContentLoaded", () => {
    const accountForm = document.getElementById("edit_account_form");
    const usernameInput = document.getElementById("username");
    const feedback = document.getElementById("username-feedback");
    const checkUsernameUrl =  accountForm.dataset.checkUrl;
    const currentUserId = accountForm.dataset.currentUserId;
    const errorsDiv = accountForm.querySelector(".field-errors");
    let currentUsername = usernameInput.value;
    let isValidUsername = false;

    // التحقق من صلاحية المعرف أثناء الكتابة
    usernameInput.addEventListener("keyup", async function () {
        isValidUsername = await validateUsername(this, feedback, checkUsernameUrl, currentUserId);
    });
    // التعامل مع نتيجة الدالة الخاصة بتعديل بيانات الحساب
    accountForm.addEventListener("submit", function(event) {

        event.preventDefault(); 
        const formData = new FormData(accountForm);
        // إذا المستخدم لم يغيّر المعرف، اعتبره صالح تلقائيًا
        if (usernameInput.value === currentUsername) {
            isValidUsername = true;
        }
        if (!isValidUsername) {
            event.preventDefault();
            feedback.innerText = "الرجاء اختيار معَرف صالح اولاً .";
            feedback.style.color = "red";
            return;
        }

        fetch(accountForm.action, {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                errorsDiv.hidden = true;
                currentUsername = data.username;
                isValidUsername = true;
                showToast("success-toast", data.message);
            } else {
                errorsDiv.innerText = data.errors
                    ? Object.values(data.errors)
                        .flat()
                        .map(error => error.message)
                        .join(" ")
                    : data.message;

                errorsDiv.hidden = false;
            }
        })
        .catch(error => {
            errorsDiv.innerText = "حدث خطأ غير متوقع.";
            errorsDiv.hidden = false;
        });            
    });
});
// ====================================================================================
// كود التحكم بفورم تغيير كلمة المرور
document.addEventListener("DOMContentLoaded", () => {
    const passwordForm = document.getElementById("change_password_form");
    const errorsDiv = passwordForm.querySelector(".field-errors");

    // استقبال نتيجة تغيير كلمة المرور.
    passwordForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        errorsDiv.hidden = true;
        errorsDiv.textContent = "";

        try {
            const response = await fetch(passwordForm.action, {
                method: "POST",
                body: new FormData(passwordForm)
            });

            const data = await response.json();

            if (data.status === "success") {
                passwordForm.reset();
                showToast("success-toast", data.message);
            } else {
                errorsDiv.textContent = data.errors
                    ? Object.values(data.errors)
                        .flat()
                        .map(error => error.message)
                        .join(" ")
                    : data.message;

                errorsDiv.hidden = false;
            }
        } catch {
            errorsDiv.textContent = "حدث خطأ غير متوقع.";
            errorsDiv.hidden = false;
        }
    });
});
// ====================================================================================
// إظهار أو إخفاء كلمة المرور عند النقر على ايقونة العين.
document.querySelectorAll("#change_password_form .trigger-password").forEach(icon => {
    icon.addEventListener("click", () => {
        const input = icon.closest(".input").querySelector("input");

        const isPassword = input.type === "password";
        input.type = isPassword ? "text" : "password";

        icon.classList.toggle("fa-eye", !isPassword);
        icon.classList.toggle("fa-eye-slash", isPassword);
    });
});
// ====================================================================================
