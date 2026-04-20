document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("edit_account_form");
    const usernameInput = document.getElementById("username");
    const feedback = document.getElementById("username-feedback");
    const checkUsernameUrl =  form.dataset.checkUrl;
    const currentUserId = form.dataset.currentUserId;
    const dialog = document.getElementById("edit_account");
    const errorsDiv = document.getElementById("errors");
    const currentUsername = usernameInput.value;
    let timeout = null;
    let isValidUsername = false;

    // التحقق من صلاحية المعرف أثناء الكتابة
    usernameInput.addEventListener("keyup", async function () {
        isValidUsername = await validateUsername(this, feedback, checkUsernameUrl, currentUserId);
    });
    // التعامل مع نتيجة الدالة الخاصة بتعديل بيانات الحساب
    form.addEventListener("submit", function(event) {
        event.preventDefault(); 
        const formData = new FormData(form);
        const url = form.action;
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

        fetch(url, {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                // ✅ نجاح: أغلق الديالوج وأظهر رسالة نجاح
                dialog.close();
                showToast("success-toast", data.message);
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                // ❌ خطأ: أبقي الديالوج مفتوح وأعرض الأخطاء
                errorsDiv.innerText = data.message;
                errorsDiv.style.display = "block";
            }
        })
        .catch(error => {
            errorsDiv.innerText = "حدث خطأ غير متوقع.";
        });            
    });
});