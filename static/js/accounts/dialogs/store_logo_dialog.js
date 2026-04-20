document.addEventListener("DOMContentLoaded", () => {
    const dropZone = document.getElementById("drop_zone");
    const fileInput = document.getElementById("file_input");
    const previewContainer = document.getElementById("preview_container");
    const preview = document.getElementById("preview");
    const form = document.getElementById("logo_form");
    const submitBtn = form.querySelector("button[type='submit']");

    let compressedFile = null;

    // Drag & Drop
    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.style.background = "#f0f0f0";
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.style.background = "";
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.style.background = "";
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        handleFile(file);
    });

    // Handle File
    function handleFile(file) {
        if (!file) {
            previewContainer.style.display = "none";
            preview.src = "";
            compressedFile = null;
            return;
        }

        if (!file.type.startsWith("image/")) {
            showToast("failed-toast", "يرجى اختيار صورة فقط");
            fileInput.value = "";
            previewContainer.style.display = "none";
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showToast("failed-toast", "حجم الصورة كبير (أقصى حجم 10MB)");
            fileInput.value = "";
            previewContainer.style.display = "none";
            return;
        }

        const reader = new FileReader();

        reader.onload = (e) => {
            preview.src = e.target.result;
            previewContainer.style.display = "block";
        };

        reader.readAsDataURL(file);

        compressImage(file);
    }

    // Submit Form
    if (!form) return;

    form.onsubmit = async function (e) {
        e.preventDefault();

        const url = form.action;

        if (!compressedFile) {
            showToast("failed-toast", "يرجى اختيار صورة");
            return;
        }

        // 🚀 تحسين UX أثناء الإرسال
        submitBtn.disabled = true;
        submitBtn.innerText = "جاري الحفظ...";
        submitBtn.style.opacity = "0.6";

        let formData = new FormData();
        formData.append(
            "csrfmiddlewaretoken",
            document.querySelector('[name=csrfmiddlewaretoken]').value
        );
        formData.append("logo", compressedFile);

        let res = await fetch(url, {
            method: "POST",
            body: formData
        });

        let data = await res.json();

        // 🔁 رجّع الزر لحالته الطبيعية
        submitBtn.disabled = false;
        submitBtn.innerText = "حفظ";
        submitBtn.style.opacity = "1";

        if (data.status === "success") {
            document.getElementById("store_logo").src = data.logo_url;
            showToast("success-toast", "تم تحديث صورة المتجر بنجاح");
            logo_dialog.close();
        }
    };

    // Compress Image
    function compressImage(file) {
        const img = new Image();
        const reader = new FileReader();

        reader.onload = (e) => {
            img.src = e.target.result;
        };

        img.onload = () => {
            const canvas = document.createElement("canvas");

            const maxWidth = 500;
            let width = img.width;
            let height = img.height;

            if (width > maxWidth) {
                height *= maxWidth / width;
                width = maxWidth;
            }
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0, width, height);

            canvas.toBlob((blob) => {
                compressedFile = new File([blob], file.name, {
                    type: "image/jpeg",
                    lastModified: Date.now()
                });
            }, "image/jpeg", 0.7);
        };
        reader.readAsDataURL(file);
    }

});