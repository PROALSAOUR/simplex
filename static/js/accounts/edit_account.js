document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("edit_account_form");
    const usernameInput = document.getElementById("username");
    const feedback = document.getElementById("username-feedback");
    const checkUsernameUrl =  form.dataset.checkUrl;
    const currentUserId = form.dataset.currentUserId;
    const errorsDiv = document.getElementById("field-errors");
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
                // ✅ نجاح: أظهر رسالة نجاح
                errorsDiv.classList.add('hidden');
                showToast("success-toast", data.message);
            } else {
                // ❌ خطأ: أعرض الأخطاء
                errorsDiv.innerText = data.message;
                errorsDiv.classList.remove('hidden');
            }
        })
        .catch(error => {
            errorsDiv.classList.remove('hidden');
            errorsDiv.innerText = "حدث خطأ غير متوقع.";
        });            
    });
});