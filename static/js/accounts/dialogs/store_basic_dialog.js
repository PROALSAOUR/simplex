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
            basic_dialog.close();
            showToast("success-toast", data.message);
        } else {
            const firstError = Object.values(data.errors)[0][0];
            showToast("failed-toast", firstError);
        }
        
    };
});