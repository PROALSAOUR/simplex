document.addEventListener("DOMContentLoaded", function () {
    let form = null;
    const orderInput = document.getElementById("images_order");
    const uploadBox = document.getElementById("uploadBox");
    const fileInput = document.getElementById("fileInput");
    const imagesList = document.getElementById("imagesList");
    const thumbnailInput = document.getElementById("id_thumbnail_img");
    const customUploadBox = document.getElementById("custom_upload_box");
    const thumbnailPreviewBox = document.getElementById("thumbnail_preview_box");
    const thumbnailPreviewCurrentBox = document.getElementById("thumbnail_preview_current_box");
    const thumbnailCurrentPreviewImg = document.getElementById("thumbnail_current_preview");
    const thumbnailPreviewNewBox = document.getElementById("thumbnail_preview_new_box");
    const thumbnailPreviewImg = document.getElementById("thumbnail_preview");
    const changeImageBtn = document.getElementById("change_image_btn");
    const resetBtn = document.getElementById("reset_form_btn");
    const MAX_FILES = 30;
    const MAX_SIZE_MB = 10;
    let uploadedFiles = [];
    const uploadedFileKeys = new Set();
    let existingImages = [];
    const existingImageKeys = new Set();
    let deletedImages = [];

    function getFormFromTarget(target) {
        if (!target) {
            return null;
        }
        if (typeof target === "string") {
            return document.getElementById(target) || document.querySelector(target);
        }
        return target instanceof HTMLFormElement ? target : null;
    }

    function setForm(target) {
        const formElement = getFormFromTarget(target);
        if (!formElement) {
            return;
        }
        if (form === formElement) {
            return;
        }
        if (form) {
            form.removeEventListener("submit", handleFormSubmit);
        }
        form = formElement;
        bindFormPersistence();
        if (form) {
            form.addEventListener("submit", handleFormSubmit);
        }
    }

    function loadInitialImages() {
        if (window.SimplexInitialImages && Array.isArray(window.SimplexInitialImages)) {
            existingImages = window.SimplexInitialImages.map(img => ({
                id: img.id,
                url: img.url,
                name: img.name,
                size: img.size,
                priority: img.priority,
                isExisting: true,
            }));
            existingImageKeys.clear();
            existingImages.forEach((img) => {
                existingImageKeys.add(`${img.name}|${img.size}`);
            });
        }
    }

    function getFileKey(file) {
        return `${file.name}|${file.size}|${file.type}|${file.lastModified}`;
    }

    function getExistingImageKey(name, size) {
        return `${name}|${size}`;
    }

    function syncFilesToForm() {
        if (!form || !orderInput) {
            return;
        }

        document.querySelectorAll(".dynamic-file").forEach((input) => input.remove());

        // Update deleted images field
        const deletedInput = form.querySelector('input[name="deleted_images"]');
        if (deletedInput) {
            deletedInput.value = JSON.stringify(deletedImages);
        }

        uploadedFiles.forEach((file) => {
            const dt = new DataTransfer();
            dt.items.add(file);

            const input = document.createElement("input");
            input.type = "file";
            input.name = "images";
            input.classList.add("dynamic-file");
            input.style.display = "none";
            input.tabIndex = -1;
            input.files = dt.files;
            form.appendChild(input);
        });

        const allImages = [...existingImages, ...uploadedFiles];
        const order = allImages.map((image, index) => ({
            id: image.id || null,
            name: image.name,
            index: index + 1,
            isExisting: image.isExisting || false,
        }));

        orderInput.value = JSON.stringify(order);
    }

    function showExistingThumbnail(url) {
        if (!thumbnailPreviewBox || !thumbnailPreviewCurrentBox || !thumbnailCurrentPreviewImg || !customUploadBox || !url) {
            return;
        }
        thumbnailCurrentPreviewImg.src = url;
        thumbnailPreviewCurrentBox.style.display = "block";
        thumbnailPreviewBox.style.display = "block";
        customUploadBox.style.display = "none";
    }

    function resetThumbnailPreview() {
        if (!thumbnailInput || !customUploadBox || !thumbnailPreviewBox || !thumbnailPreviewImg) {
            return;
        }

        thumbnailInput.value = "";
        thumbnailPreviewImg.src = "";
        if (thumbnailPreviewNewBox) {
            thumbnailPreviewNewBox.style.display = "none";
        }

        if (window.SimplexInitialThumbnailUrl) {
            customUploadBox.style.display = "none";
            showExistingThumbnail(window.SimplexInitialThumbnailUrl);
        } else {
            customUploadBox.style.display = "block";
            thumbnailPreviewBox.style.display = "none";
        }
    }

    function resetImages() {
        uploadedFiles = [];
        uploadedFileKeys.clear();
        existingImages = [];
        deletedImages = [];
        renderImages();
        syncFilesToForm();
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
                resetImages();
                resetThumbnailPreview();

                if (window.SimplexColorManager?.resetColors) {
                    window.SimplexColorManager.resetColors();
                } else {
                    const colorsField = document.getElementById("colors_data");
                    const colorsList = document.getElementById("colors-list");
                    if (colorsField) {
                        colorsField.value = "";
                    }
                    if (colorsList) {
                        colorsList.innerHTML = "";
                    }
                }
            });
        }
    }

    function initThumbnailPreview() {
        if (!thumbnailInput || !customUploadBox || !thumbnailPreviewBox || !thumbnailPreviewImg || !changeImageBtn) {
            return;
        }

        if (window.SimplexInitialThumbnailUrl) {
            showExistingThumbnail(window.SimplexInitialThumbnailUrl);
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

    function updateThumbPreview(file) {
        if (!file) {
            return;
        }
        const url = URL.createObjectURL(file);
        thumbnailPreviewImg.src = url;
        if (thumbnailPreviewNewBox) {
            thumbnailPreviewNewBox.style.display = "block";
        }
        if (thumbnailPreviewBox) {
            thumbnailPreviewBox.style.display = "block";
        }
        customUploadBox.style.display = "none";
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

    async function processFile(file, batchKeys) {
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
        const existingKey = getExistingImageKey(file.name, file.size);
        if (
            uploadedFileKeys.has(key) ||
            batchKeys.has(key) ||
            existingImageKeys.has(existingKey)
        ) {
            showToast("failed-toast", `${file.name} مكررة`);
            return null;
        }

        batchKeys.add(key);
        return compressImage(file, key);
    }

    async function addFiles(files) {
        if (!files || files.length === 0) {
            return;
        }
        const batchKeys = new Set();
        const results = await Promise.all([...files].map((file) => processFile(file, batchKeys)));
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

        const allImages = [...existingImages, ...uploadedFiles];

        if (allImages.length > 0) {
            uploadBox.classList.add("hidden");
        } else {
            uploadBox.classList.remove("hidden");
        }

        allImages.forEach((image, index) => {
            const url = image.isExisting ? image.url : URL.createObjectURL(image);
            const item = document.createElement("div");
            item.className = "image-item";
            item.draggable = true;

            item.innerHTML = `
                <div class="drag-handle">☰</div>
                <div class="image-number">${index + 1}</div>
                <img src="${url}" class="image-preview">
                <div class="image-info">
                    <p><strong>${image.name}</strong></p>
                    ${image.isExisting ? '<p>صورة موجودة</p>' : `<p>الحجم: ${(image.size / 1024).toFixed(1)} KB</p><p>النوع: ${image.type}</p>`}
                </div>
                <button type="button" class="remove-btn">إزالة</button>
            `;

            item.querySelector(".remove-btn").addEventListener("click", () => {
                if (image.isExisting) {
                    existingImages.splice(existingImages.indexOf(image), 1);
                    deletedImages.push(image.id);
                    existingImageKeys.delete(getExistingImageKey(image.name, image.size));
                } else {
                    const removed = uploadedFiles.splice(uploadedFiles.indexOf(image), 1)[0];
                    if (removed && removed.uploadKey) {
                        uploadedFileKeys.delete(removed.uploadKey);
                    }
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

        if (allImages.length > 0) {
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
        const newExisting = [];
        const newUploaded = [];

        items.forEach((item) => {
            const name = item.querySelector("strong")?.innerText;
            const existingImg = existingImages.find((img) => img.name === name);
            const uploadedImg = uploadedFiles.find((img) => img.name === name);
            if (existingImg) {
                newExisting.push(existingImg);
            } else if (uploadedImg) {
                newUploaded.push(uploadedImg);
            }
        });

        existingImages = newExisting;
        uploadedFiles = newUploaded;
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

    function handleFormSubmit(event) {
        const hasExisting = existingImages && existingImages.length > 0;
        const hasNew = uploadedFiles && uploadedFiles.length > 0;

        if (!hasExisting && !hasNew) {
            event.preventDefault();
            showToast('failed-toast', 'يرجى اضافة صور للمنتج اولا!');
            return;
        }

        syncFilesToForm();
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
        loadInitialImages();
        restoreFormData();
        initThumbnailPreview();
        initFileUploader();
        bindDragSort();
        renderImages(); // Render initial images
    }

    setForm("add_product_form");
    init();

    window.SimplexImageManager = {
        setForm,
        resetImages,
        resetThumbnailPreview,
        syncFilesToForm,
    };
});