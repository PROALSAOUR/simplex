document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("basic_form");
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
            document.getElementById("store_name").innerText = data.name;
            document.getElementById("store_location").innerText = data.location;
            document.getElementById("store_check_orders").innerText = data.check_orders;
            document.getElementById("store_status").innerText = data.store_status;
            basic_dialog.close();
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
        
    };
});