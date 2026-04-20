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
            showToast("success-toast", data.message);
        } else {
            showToast("failed-toast", data.message);
        }
        basic_dialog.close();
    };
});