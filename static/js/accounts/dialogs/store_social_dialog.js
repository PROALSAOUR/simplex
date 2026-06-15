document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("social_form");
    if (!form) return;
    form.onsubmit = async function(e) {
        e.preventDefault();
        const url = form.action;
        let formData = new FormData(this);
        let res = await fetch(url, {
            method: "POST",
            body: formData
        });
        let data = await res.json();
        if (data.status === "success") {
            document.getElementById("store_telegram").innerText = data.telegram || "لم تتم الإضافة بعد";
            document.getElementById("store_phone_number1").innerText = data.phone_number1 || "لم تتم الإضافة بعد";
            document.getElementById("store_facebook").innerText = data.facebook || "لم تتم الإضافة بعد";
            document.getElementById("store_instagram").innerText = data.instagram || "لم تتم الإضافة بعد";
            document.getElementById("store_tiktok").innerText = data.tiktok || "لم تتم الإضافة بعد";
            showToast("success-toast", data.message);
        } else {
            let errorMessage = data.message || "حدث خطأ ما";
            if (data.errors && typeof data.errors === 'object') {
                // الحصول على أول خطأ من الأخطاء
                const errorFields = Object.keys(data.errors);
                if (errorFields.length > 0) {
                    const firstErrorField = errorFields[0];
                    const errorArray = data.errors[firstErrorField];
                    if (Array.isArray(errorArray) && errorArray.length > 0) {
                        errorMessage = errorArray[0];
                    } else if (typeof errorArray === 'string') {
                        errorMessage = errorArray;
                    }
                }
            }
            showToast("failed-toast", errorMessage);
        }
        social_dialog.close();
    };
});