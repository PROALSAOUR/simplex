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
            document.getElementById("store_telegram").innerText = data.telegram;
            document.getElementById("store_facebook").innerText = data.facebook;
            document.getElementById("store_instagram").innerText = data.instagram;
            document.getElementById("store_tiktok").innerText = data.tiktok;
            showToast("success-toast", data.message);
        } else {
            showToast("failed-toast", data.message);
        }
        social_dialog.close();
    };
});