document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("add_product_form");
    const resetBtn = document.getElementById("reset_form_btn");
    const orderInput = document.getElementById("images_order");
    const offerCheckbox = document.getElementById("id_offer");
    const offerCheckboxField = document.getElementById("offer_checkbox_field");
    const priceInput = document.getElementById("id_price");
    const offerPriceInput = document.getElementById("id_offer_price");
    const priceField = document.getElementById("price_field");
    const offerPriceField = document.getElementById("offer_price_field");
    const offerPercentage = document.getElementById("offer_percentage");
    const uploadBox = document.getElementById("uploadBox");
    const fileInput = document.getElementById("fileInput");
    const imagesList = document.getElementById("imagesList");
    const thumbnailInput = document.getElementById("id_thumbnail_img");
    const customUploadBox = document.getElementById("custom_upload_box");
    const thumbnailPreviewBox = document.getElementById("thumbnail_preview_box");
    const thumbnailPreviewImg = document.getElementById("thumbnail_preview");
    const changeImageBtn = document.getElementById("change_image_btn");
    const MAX_FILES = 30;
    const MAX_SIZE_MB = 10;
    let uploadedFiles = [];
    const uploadedFileKeys = new Set();

    function getFileKey(file) {
        return `${file.name}|${file.size}|${file.type}|${file.lastModified}`;
    }

    function initOfferControls() {
        if (!offerCheckbox || !offerCheckboxField || !priceInput || !offerPriceInput || !priceField || !offerPriceField || !offerPercentage) {
            return;
        }

        const priceLabel = priceField.querySelector("label");
        const originalNextSibling = priceField.nextElementSibling;

        function setOfferState(isEnabled) {
            if (isEnabled) {
                priceLabel.textContent = "السعر قبل التخفيض";
                offerPriceField.style.display = "block";
                offerPriceInput.required = true;
                offerCheckboxField.after(priceField);
                priceField.after(offerPriceField);
                calculateDiscount();
                return;
            }

            priceLabel.textContent = "سعر البيع";
            offerPriceField.style.display = "none";
            offerPercentage.style.display = "none";
            offerPriceInput.value = "";
            offerPriceInput.required = false;

            if (originalNextSibling) {
                originalNextSibling.before(priceField);
            }
        }

        function calculateDiscount() {
            const originalPrice = parseFloat(priceInput.value);
            const discountedPrice = parseFloat(offerPriceInput.value);

            if (isNaN(originalPrice) || isNaN(discountedPrice)) {
                offerPercentage.style.display = "none";
                offerPriceInput.setCustomValidity("");
                return;
            }

            if (discountedPrice >= originalPrice) {
                offerPriceInput.setCustomValidity("يجب أن يكون السعر بعد التخفيض أقل من السعر قبل التخفيض");
                offerPriceInput.reportValidity();
                offerPercentage.style.display = "none";
                return;
            }

            offerPriceInput.setCustomValidity("");
            const percentage = ((originalPrice - discountedPrice) / originalPrice) * 100;
            offerPercentage.style.display = "inline-block";
            offerPercentage.textContent = "نسبة التخفيض " + percentage.toFixed(1) + "%";
        }

        offerCheckbox.addEventListener("change", function () {
            setOfferState(this.checked);
        });

        priceInput.addEventListener("input", calculateDiscount);
        offerPriceInput.addEventListener("input", calculateDiscount);

        setOfferState(offerCheckbox.checked);
    }

    function syncFilesToForm() {
        if (!form || !orderInput) {
            return;
        }

        document.querySelectorAll(".dynamic-file").forEach((input) => input.remove());

        uploadedFiles.forEach((file) => {
            const dt = new DataTransfer();
            dt.items.add(file);

            const input = document.createElement("input");
            input.type = "file";
            input.name = "images";
            input.classList.add("dynamic-file");
            input.files = dt.files;
            form.appendChild(input);
        });

        const order = uploadedFiles.map((file, index) => ({
            name: file.name,
            index: index + 1,
        }));

        orderInput.value = JSON.stringify(order);
    }

    function resetFormStorage() {
        if (!form) {
            return;
        }

        for (const field of form.elements) {
            if (!field.name) {
                continue;
            }
            sessionStorage.removeItem(field.name);
        }
    }

    function restoreFormData() {
        if (!form) {
            return;
        }

        for (const field of form.elements) {
            if (!field.name || field.type === "file") {
                continue;
            }
            const savedValue = sessionStorage.getItem(field.name);
            if (savedValue !== null) {
                field.value = savedValue;
            }
        }
    }

    function bindFormPersistence() {
        if (!form) {
            return;
        }

        form.addEventListener("input", (event) => {
            const field = event.target;
            if (!field.name || field.type === "file") {
                return;
            }
            sessionStorage.setItem(field.name, field.value);
        });

        form.addEventListener("submit", () => {
            resetFormStorage();
        });

        if (resetBtn) {
            resetBtn.addEventListener("click", () => {
                form.reset();
                resetFormStorage();
            });
        }
    }

    function initThumbnailPreview() {
        if (!thumbnailInput || !customUploadBox || !thumbnailPreviewBox || !thumbnailPreviewImg || !changeImageBtn) {
            return;
        }

        function updateThumbPreview(file) {
            if (!file) {
                return;
            }
            const url = URL.createObjectURL(file);
            thumbnailPreviewImg.src = url;
            customUploadBox.style.display = "none";
            thumbnailPreviewBox.style.display = "block";
        }

        thumbnailInput.addEventListener("change", function () {
            const file = this.files[0];
            if (file) {
                updateThumbPreview(file);
            }
        });

        changeImageBtn.addEventListener("click", function () {
            thumbnailInput.click();
        });
    }

    function initFileUploader() {
        if (!uploadBox || !fileInput || !imagesList) {
            return;
        }

        uploadBox.addEventListener("click", () => fileInput.click());

        fileInput.addEventListener("change", (event) => {
            addFiles(event.target.files);
        });

        uploadBox.addEventListener("dragover", (event) => {
            event.preventDefault();
            uploadBox.classList.add("dragover");
        });

        uploadBox.addEventListener("dragleave", () => {
            uploadBox.classList.remove("dragover");
        });

        uploadBox.addEventListener("drop", (event) => {
            event.preventDefault();
            uploadBox.classList.remove("dragover");
            addFiles(event.dataTransfer.files);
        });
    }

    async function processFile(file) {
        if (!file.type.startsWith("image/")) {
            showToast("failed-toast", `${file.name} ليس صورة`);
            return null;
        }

        const sizeMB = file.size / (1024 * 1024);
        if (sizeMB > MAX_SIZE_MB) {
            showToast("failed-toast", `${file.name} أكبر من الحد`);
            return null;
        }

        const key = getFileKey(file);
        if (uploadedFileKeys.has(key)) {
            showToast("failed-toast", `${file.name} مكررة`);
            return null;
        }

        return compressImage(file, key);
    }

    async function addFiles(files) {
        if (!files || files.length === 0) {
            return;
        }
        const results = await Promise.all([...files].map(processFile));
        results.forEach((file) => {
            if (file) {
                uploadedFiles.push(file);
                uploadedFileKeys.add(file.uploadKey);
            }
        });
        renderImages();
    }

    function renderImages() {
        if (!imagesList || !uploadBox) {
            return;
        }

        imagesList.innerHTML = "";

        if (uploadedFiles.length > 0) {
            uploadBox.classList.add("hidden");
        } else {
            uploadBox.classList.remove("hidden");
        }

        uploadedFiles.forEach((file, index) => {
            const url = URL.createObjectURL(file);
            const item = document.createElement("div");
            item.className = "image-item";
            item.draggable = true;

            item.innerHTML = `
                <div class="drag-handle">☰</div>
                <div class="image-number">${index + 1}</div>
                <img src="${url}" class="image-preview">
                <div class="image-info">
                    <p><strong>${file.name}</strong></p>
                    <p>الحجم: ${(file.size / 1024).toFixed(1)} KB</p>
                    <p>النوع: ${file.type}</p>
                </div>
                <button type="button" class="remove-btn">إزالة</button>
            `;

            item.querySelector(".remove-btn").addEventListener("click", () => {
                const removed = uploadedFiles.splice(index, 1)[0];
                if (removed && removed.uploadKey) {
                    uploadedFileKeys.delete(removed.uploadKey);
                }
                renderImages();
            });

            item.addEventListener("dragstart", () => item.classList.add("dragging"));
            item.addEventListener("dragend", () => {
                item.classList.remove("dragging");
                updateOrder();
            });

            imagesList.appendChild(item);
        });

        if (uploadedFiles.length > 0) {
            const miniUpload = document.createElement("div");
            miniUpload.className = "mini-upload";
            miniUpload.innerHTML = `
                <input type="file" multiple accept="image/*">
                <p>+ إضافة المزيد</p>
            `;

            const extraInput = miniUpload.querySelector("input");
            miniUpload.addEventListener("click", () => extraInput.click());
            extraInput.addEventListener("change", (event) => addFiles(event.target.files));
            miniUpload.addEventListener("dragover", (event) => event.preventDefault());
            miniUpload.addEventListener("drop", (event) => {
                event.preventDefault();
                addFiles(event.dataTransfer.files);
            });

            imagesList.appendChild(miniUpload);
        }
    }

    function updateOrder() {
        if (!imagesList) {
            return;
        }

        const items = [...imagesList.querySelectorAll(".image-item")];
        const newOrder = [];

        items.forEach((item) => {
            const name = item.querySelector("strong")?.innerText;
            const file = uploadedFiles.find((existing) => existing.name === name);
            if (file) {
                newOrder.push(file);
            }
        });

        uploadedFiles = newOrder;
        renderImages();
    }

    function compressImage(file, uploadKey) {
        return new Promise((resolve) => {
            const img = new Image();
            const reader = new FileReader();

            reader.onload = (event) => {
                img.src = event.target.result;
            };

            img.onload = () => {
                const canvas = document.createElement("canvas");
                const maxWidth = 800;
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
                canvas.toBlob(
                    (blob) => {
                        const compressedFile = new File([blob], file.name, {
                            type: "image/jpeg",
                            lastModified: Date.now(),
                        });
                        compressedFile.uploadKey = uploadKey;
                        resolve(compressedFile);
                    },
                    "image/jpeg",
                    0.7
                );
            };

            reader.readAsDataURL(file);
        });
    }

    function bindDragSort() {
        if (!imagesList) {
            return;
        }

        imagesList.addEventListener("dragover", (event) => {
            event.preventDefault();
            const draggingItem = document.querySelector(".dragging");
            if (!draggingItem) {
                return;
            }

            const items = [...imagesList.querySelectorAll(".image-item:not(.dragging)")];
            let nextSibling = null;

            for (const item of items) {
                const rect = item.getBoundingClientRect();
                const mid = rect.top + rect.height / 2;
                if (event.clientY < mid) {
                    nextSibling = item;
                    break;
                }
            }

            if (nextSibling) {
                imagesList.insertBefore(draggingItem, nextSibling);
            } else if (items.length > 0) {
                items[items.length - 1].after(draggingItem);
            }
        });
    }

    function init() {
        restoreFormData();
        bindFormPersistence();
        initThumbnailPreview();
        initOfferControls();
        initFileUploader();
        bindDragSort();

        if (form) {
            form.addEventListener("submit", syncFilesToForm);
        }
    }
    init();
});
