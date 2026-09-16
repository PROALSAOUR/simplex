// JavaScript code for managing product images 

document.addEventListener("DOMContentLoaded", function () {
    // ============================================================
    // إدارة صور المنتج

    let imagePrototype = null;
    let miniUpload = null;
    let helpText = null;

    let existingImages = [];
    let uploadedFiles = [];

    let initialExistingImages = [];
    let existingImageKeys = new Set();

    let deletedImageIds = [];


    // ============================================================
    // العناصر الرئيسية

    const uploadBox = document.getElementById("uploadBox");
    const fileInput = document.getElementById("fileInput");
    const imagesPreviewBox = document.getElementById("images_preview_box");
    const imagesList = document.getElementById("imagesList");

    const imagesOrderInput = document.getElementById("images_order");
    const deletedImagesInput = document.getElementById("deleted_images");

    // ============================================================
    // تجهيز الـ Prototypes
    function prepareImageTemplate() {
        // فصل نماذج الصور والإضافات عن العناصر المعروضة فعلياً
        if (!imagesList) {
            return;
        }

        const firstItem = imagesList.querySelector(".image-item");
        const originalMiniUpload = imagesList.querySelector(".mini-upload");
        const originalHelpText = imagesList.querySelector(".help-text");

        if (firstItem) {
            imagePrototype = firstItem.cloneNode(true);
            firstItem.remove();
        }

        if (originalMiniUpload) {
            miniUpload = originalMiniUpload.cloneNode(true);
            originalMiniUpload.remove();
        }

        if (originalHelpText) {
            helpText = originalHelpText.cloneNode(true);
            originalHelpText.remove();
        }
    }

    // ============================================================
    // تحميل الصور الموجودة مسبقاً
    function loadInitialImages() {
        // تحميل الصور الموجودة مسبقاً في المنتج
        if (!Array.isArray(window.SimplexInitialImages)) {
            existingImages = [];
            initialExistingImages = [];
            return;
        }

        existingImages = window.SimplexInitialImages.map((image) => ({
            ...image,
            type: "existing"
        }));

        initialExistingImages = existingImages.map((image) => ({
            ...image
        }));

        existingImageKeys = new Set(
            existingImages.map((image) =>
                getExistingImageKey(image.name, image.size)
            )
        );
    }

    // ============================================================
    // إنشاء مفتاح للملف المرفوع
    function getFileKey(file) {
        // إنشاء مفتاح ثابت للملف مع الحفاظ على مفتاحه الأصلي بعد الضغط
        if (file._originalKey) {
            return file._originalKey;
        }

        return `${file.name}|${file.size}|${file.type}|${file.lastModified}`;
    }

    // ============================================================
    // إنشاء مفتاح للصورة الموجودة
    function getExistingImageKey(name, size) {
        // إنشاء مفتاح للصورة الموجودة مسبقاً
        return `${name}|${size}`;
    }

    // ============================================================
    // الحصول على جميع الصور
    function getAllImages() {
        // دمج الصور الموجودة مع الصور الجديدة
        return [
            ...existingImages,
            ...uploadedFiles
        ];
    }

    // ============================================================
    // مزامنة الملفات مع Form
    function syncFilesToForm() {
        // مزامنة الصور الجديدة وترتيبها مع حقول النموذج
        const form = fileInput?.form;

        if (!form) {
            return;
        }

        form
            .querySelectorAll(".dynamic-file")
            .forEach((input) => input.remove());

        if (deletedImagesInput) {
            deletedImagesInput.value = deletedImageIds.join(",");
        }

        uploadedFiles.forEach((file) => {
            const input = document.createElement("input");

            input.type = "file";
            input.name = "images";
            input.className = "dynamic-file";
            input.hidden = true;

            const dataTransfer = new DataTransfer();

            dataTransfer.items.add(file);

            input.files = dataTransfer.files;

            form.appendChild(input);
        });

        const order = getAllImages().map((image) => {
            if (image.type === "existing") {
                return {
                    type: "existing",
                    id: image.id
                };
            }

            return {
                type: "uploaded",
                key: getFileKey(image)
            };
        });

        if (imagesOrderInput) {
            imagesOrderInput.value = JSON.stringify(order);
        }
    }

    // ============================================================
    // تحميل الصورة الرئيسية الموجودة مسبقاً
    function loadInitialThumbnail() {
        // تحميل الصورة الرئيسية الموجودة وإخفاء مربع الرفع
        const thumbnailPreviewBox =
            document.getElementById("thumbnail_preview_box");

        const thumbnailImage =
            thumbnailPreviewBox?.querySelector(".image-preview");

        const thumbnailInput =
            document.getElementById("id_thumbnail_img");

        const uploadLabel =
            document.getElementById("custom_upload_box");

        if (
            !thumbnailPreviewBox ||
            !thumbnailImage ||
            !window.SimplexInitialThumbnailUrl
        ) {
            return;
        }

        thumbnailImage.src =
            window.SimplexInitialThumbnailUrl;

        thumbnailPreviewBox.style.display = "block";

        // إخفاء مربع رفع الصورة الرئيسية
        if (uploadLabel) {
            uploadLabel.style.display = "none";
        }

        if (thumbnailInput) {
            thumbnailInput.dataset.hasInitialImage = "true";
        }

        updateThumbnailInfoFromExisting();
    }

    // ============================================================
    // معلومات الصورة الرئيسية الموجودة
    function updateThumbnailInfoFromExisting() {
        // تحديث معلومات الصورة الرئيسية الموجودة مسبقاً
        const thumbnailPreviewBox =
            document.getElementById("thumbnail_preview_box");

        if (!thumbnailPreviewBox) {
            return;
        }

        const info = thumbnailPreviewBox.querySelector(".image-info");

        if (!info) {
            return;
        }

        const sizeElement = info.querySelector("p:first-child");
        const typeElement = info.querySelector("p:last-child");

        if (sizeElement) {
            sizeElement.textContent = "الحجم: الصورة الحالية";
        }

        if (typeElement) {
            typeElement.textContent = "النوع: صورة المنتج";
        }
    }

    // ============================================================
    // إعادة ضبط الصورة الرئيسية
    function resetThumbnail() {
            // إعادة الصورة الرئيسية إلى حالة الرفع الأصلية
            const thumbnailInput =
                document.getElementById("id_thumbnail_img");

            const uploadLabel =
                document.getElementById("custom_upload_box");

            const thumbnailPreviewBox =
                document.getElementById("thumbnail_preview_box");

            const thumbnailImage =
                thumbnailPreviewBox?.querySelector(".image-preview");

            if (thumbnailInput) {
                thumbnailInput.value = "";

                delete thumbnailInput.dataset.hasInitialImage;
            }

            if (thumbnailImage) {
                thumbnailImage.src = "";
            }

            if (thumbnailPreviewBox) {
                thumbnailPreviewBox.style.display = "none";
            }

            // إعادة إظهار مربع رفع الصورة الرئيسية
            if (uploadLabel) {
                uploadLabel.style.display = "";
            }
    }

    // ============================================================
    // عرض معاينة الصورة الرئيسية
    function previewThumbnail(file) {
        // عرض معاينة الصورة الرئيسية الجديدة
        const thumbnailPreviewBox =
            document.getElementById("thumbnail_preview_box");

        const thumbnailImage =
            thumbnailPreviewBox?.querySelector(".image-preview");

        const thumbnailInput =
            document.getElementById("id_thumbnail_img");

        if (
            !file ||
            !thumbnailPreviewBox ||
            !thumbnailImage
        ) {
            return;
        }

        const reader = new FileReader();

        reader.onload = function (event) {
            // عرض الصورة الجديدة داخل المعاينة
            thumbnailImage.src = event.target.result;
        };

        reader.readAsDataURL(file);

        thumbnailPreviewBox.style.display = "block";

        if (thumbnailInput) {
            delete thumbnailInput.dataset.hasInitialImage;
        }

        updateThumbnailInfo(file);
    }

    // ============================================================
    // تحديث معلومات الصورة الرئيسية
    function updateThumbnailInfo(file) {
        // تحديث حجم ونوع الصورة الرئيسية
        const thumbnailPreviewBox =
            document.getElementById("thumbnail_preview_box");

        const info =
            thumbnailPreviewBox?.querySelector(".image-info");

        if (!info) {
            return;
        }

        const sizeElement = info.querySelector("p:first-child");
        const typeElement = info.querySelector("p:last-child");

        if (sizeElement) {
            sizeElement.textContent =
                `الحجم: ${formatFileSize(file.size)}`;
        }

        if (typeElement) {
            typeElement.textContent =
                `النوع: ${file.type}`;
        }
    }

    // ============================================================
    // تنسيق حجم الملف
    function formatFileSize(size) {
        // تحويل حجم الملف إلى صيغة مناسبة للعرض
        if (size < 1024) {
            return `${size} B`;
        }

        if (size < 1024 * 1024) {
            return `${(size / 1024).toFixed(1)} KB`;
        }

        return `${(size / (1024 * 1024)).toFixed(1)} MB`;
    }

    // ============================================================
    // تهيئة رفع الصورة الرئيسية
    function initThumbnailUploader() {
        // تفعيل رفع واستبدال الصورة الرئيسية
        const thumbnailInput =
            document.getElementById("id_thumbnail_img");

        const uploadLabel =
            document.getElementById("custom_upload_box");

        const changeButton =
            document.getElementById("change_image_btn");

        if (!thumbnailInput) {
            return;
        }

        if (uploadLabel) {
            uploadLabel.addEventListener("dragover", (event) => {
                event.preventDefault();
                uploadLabel.classList.add("drag-over");
            });

            uploadLabel.addEventListener("dragleave", () => {
                uploadLabel.classList.remove("drag-over");
            });

            uploadLabel.addEventListener("drop", (event) => {
                event.preventDefault();

                uploadLabel.classList.remove("drag-over");

                const file = event.dataTransfer.files[0];

                if (file) {
                    setThumbnailFile(file);
                }
            });
        }

        thumbnailInput.addEventListener("change", () => {
            // معالجة الصورة الرئيسية عند اختيارها
            const file = thumbnailInput.files[0];

            if (file) {
                setThumbnailFile(file);
            }
        });

        if (changeButton) {
            changeButton.addEventListener("click", () => {
                // فتح اختيار صورة جديدة لاستبدال الحالية
                thumbnailInput.click();
            });
        }
    }

    // ============================================================
    // تعيين ملف الصورة الرئيسية
    function setThumbnailFile(file) {
        // التحقق من الصورة الرئيسية وتعيينها للنموذج
        if (!file.type.startsWith("image/")) {
            showToast(
                "failed-toast",
                "يرجى اختيار ملف صورة صالح."
            );

            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showToast(
                "failed-toast",
                "حجم الصورة يجب ألا يتجاوز 10 ميجابايت."
            );

            return;
        }

        const thumbnailInput =
            document.getElementById("id_thumbnail_img");

        const uploadLabel =
            document.getElementById("custom_upload_box");

        const thumbnailPreviewBox =
            document.getElementById("thumbnail_preview_box");

        if (!thumbnailInput) {
            return;
        }

        const dataTransfer = new DataTransfer();

        dataTransfer.items.add(file);

        thumbnailInput.files = dataTransfer.files;

        // إخفاء مربع رفع الصورة الرئيسية
        if (uploadLabel) {
            uploadLabel.style.display = "none";
        }

        // إظهار معاينة الصورة الرئيسية
        if (thumbnailPreviewBox) {
            thumbnailPreviewBox.style.display = "block";
        }

        previewThumbnail(file);
    }

    // ============================================================
    // تهيئة رفع الصور الإضافية
    function initFileUploader() {
        // تفعيل اختيار وسحب وإفلات الصور الإضافية
        if (!uploadBox || !fileInput) {
            return;
        }

        uploadBox.addEventListener("click", (event) => {
            // فتح اختيار الملفات عند الضغط على منطقة الرفع
            if (event.target.closest("input")) {
                return;
            }

            fileInput.click();
        });

        fileInput.addEventListener("change", () => {
            // معالجة الصور عند اختيارها من الجهاز
            addFiles(fileInput.files);

            fileInput.value = "";
        });

        uploadBox.addEventListener("dragover", (event) => {
            // السماح بسحب الصور إلى منطقة الرفع
            event.preventDefault();

            uploadBox.classList.add("drag-over");
        });

        uploadBox.addEventListener("dragleave", () => {
            // إزالة حالة السحب عند مغادرة المنطقة
            uploadBox.classList.remove("drag-over");
        });

        uploadBox.addEventListener("drop", (event) => {
            // استقبال الصور المسحوبة إلى منطقة الرفع
            event.preventDefault();

            uploadBox.classList.remove("drag-over");

            addFiles(event.dataTransfer.files);
        });
    }

    // ============================================================
    // معالجة الملفات
    async function addFiles(files) {
        // معالجة مجموعة الصور والتحقق من صلاحيتها وتكرارها
        if (!files || files.length === 0) {
            return;
        }

        const fileArray = Array.from(files);

        for (const file of fileArray) {
            await processFile(file);
        }

        renderImages();
        syncFilesToForm();
    }

    // ============================================================
    // معالجة ملف واحد
    async function processFile(file) {
        // التحقق من الملف وضغطه ثم إضافته إلى قائمة الصور
        if (!file.type.startsWith("image/")) {
            showToast(
                "failed-toast",
                `الملف "${file.name}" ليس صورة.`
            );

            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showToast(
                "failed-toast",
                `الصورة "${file.name}" تتجاوز 10 ميجابايت.`
            );

            return;
        }

        const totalImages =
            existingImages.length + uploadedFiles.length;

        if (totalImages >= 30) {
            showToast(
                "failed-toast",
                "يمكنك رفع 30 صورة كحد أقصى."
            );

            return;
        }

        const fileKey = getFileKey(file);

        const uploadedDuplicate = uploadedFiles.some(
            (uploadedFile) =>
                getFileKey(uploadedFile) === fileKey
        );

        if (uploadedDuplicate) {
            showToast(
                "failed-toast",
                `الصورة مضافة بالفعل.`
            );

            return;
        }

        const existingDuplicate =
            existingImageKeys.has(
                getExistingImageKey(file.name, file.size)
            );

        if (existingDuplicate) {
            showToast(
                "failed-toast",
                `الصورة "${file.name}" موجودة بالفعل.`
            );

            return;
        }

        const compressedFile = await compressImage(file);

        // الاحتفاظ بمفتاح الملف الأصلي حتى لا يتغير بعد الضغط
        compressedFile._originalKey = fileKey;

        uploadedFiles.push(compressedFile);
    }

    // ============================================================
    // ضغط الصورة
    function compressImage(file) {
        // ضغط الصورة مع الحفاظ على إمكانية رفعها كملف
        return new Promise((resolve) => {
            const reader = new FileReader();

            reader.onload = (event) => {
                // تحميل الصورة قبل ضغطها
                const image = new Image();

                image.onload = () => {
                    // حساب أبعاد الصورة الجديدة
                    const maxWidth = 2000;
                    const maxHeight = 2000;

                    let width = image.width;
                    let height = image.height;

                    if (
                        width > maxWidth ||
                        height > maxHeight
                    ) {
                        const ratio = Math.min(
                            maxWidth / width,
                            maxHeight / height
                        );

                        width *= ratio;
                        height *= ratio;
                    }

                    const canvas =
                        document.createElement("canvas");

                    canvas.width = width;
                    canvas.height = height;

                    const context =
                        canvas.getContext("2d");

                    context.drawImage(
                        image,
                        0,
                        0,
                        width,
                        height
                    );

                    canvas.toBlob(
                        (blob) => {
                            // إنشاء ملف جديد بعد ضغط الصورة
                            if (!blob) {
                                resolve(file);
                                return;
                            }

                            const compressedFile =
                                new File(
                                    [blob],
                                    file.name,
                                    {
                                        type:
                                            file.type ||
                                            "image/jpeg",
                                        lastModified:
                                            file.lastModified
                                    }
                                );

                            resolve(compressedFile);
                        },
                        file.type || "image/jpeg",
                        0.85
                    );
                };

                image.src = event.target.result;
            };

            reader.onerror = () => {
                // استخدام الملف الأصلي عند فشل القراءة
                resolve(file);
            };

            reader.readAsDataURL(file);
        });
    }

    // ============================================================
    // إنشاء عنصر صورة
    function createImageItem(image, index) {
        // إنشاء عنصر الصورة من Prototype الموجود في القالب
        if (!imagePrototype) {
            return null;
        }

        const item = imagePrototype.cloneNode(true);

        item.classList.add("generated-image");

        const number =
            item.querySelector(".image-number");

        const imageElement =
            item.querySelector(".image-preview");

        const info =
            item.querySelector(".image-info");

        const removeButton =
            item.querySelector(".remove-btn");

        // رقم الصورة
        if (number) {
            number.textContent = index + 1;
        }

        // تحديد نوع الصورة
        if (image.type === "existing") {
            item.dataset.imageType = "existing";
            item.dataset.imageId = image.id;
        } else {
            item.dataset.imageType = "uploaded";
            item.dataset.uploadKey = getFileKey(image);
        }

        // ------------------------------------------------------------
        // تحديد رابط المعاينة
        // ------------------------------------------------------------

        let imageUrl = "";

        if (image.type === "existing") {
            imageUrl =
                image.url ||
                image.image_url ||
                image.src ||
                image.image ||
                "";
        } else {
            imageUrl = URL.createObjectURL(image);
        }

        // وضع الصورة داخل عنصر المعاينة
        if (imageElement && imageUrl) {
            imageElement.src = imageUrl;

            imageElement.alt =
                image.name ||
                `صورة المنتج ${index + 1}`;
        }

        // ------------------------------------------------------------
        // معلومات الصورة
        // ------------------------------------------------------------

        if (info) {
            const infoElements =
                info.querySelectorAll("p");

            if (infoElements[0]) {
                if (image.size) {
                    infoElements[0].textContent =
                        `الحجم: ${formatFileSize(image.size)}`;
                } else {
                    infoElements[0].textContent =
                        "الحجم: غير معروف";
                }
            }

            if (infoElements[1]) {
                const imageType =
                    image.mime_type ||
                    image.file_type ||
                    image.content_type ||
                    image.type;

                infoElements[1].textContent =
                    `النوع: ${
                        imageType === "existing"
                            ? "صورة"
                            : imageType || "صورة"
                    }`;
            }
        }

        // ------------------------------------------------------------
        // زر الحذف
        // ------------------------------------------------------------

        if (removeButton) {
            removeButton.addEventListener("click", () => {
                // حذف الصورة المحددة من قائمة الصور
                removeImage(item);
            });
        }

        // ------------------------------------------------------------
        // السحب والترتيب
        // ------------------------------------------------------------

        item.draggable = true;

        item.addEventListener("dragstart", () => {
            // تحديد الصورة التي يتم سحبها
            item.classList.add("dragging");
        });

        item.addEventListener("dragend", () => {
            // إنهاء السحب وحفظ الترتيب الجديد
            item.classList.remove("dragging");

            updateOrderFromDOM();
            updateImageNumbers();
            syncFilesToForm();
        });

        return item;
    }

    // ============================================================
    // رسم الصور
    function renderImages() {
        // إعادة رسم قائمة الصور والتحكم في ظهور صندوق الرفع والمعاينة
        if (!imagesList) {
            return;
        }

        // حذف العناصر التي أنشأها JavaScript في الرسم السابق
        imagesList
            .querySelectorAll(".image-item.generated-image")
            .forEach((item) => item.remove());

        imagesList
            .querySelectorAll(".mini-upload.generated-mini-upload")
            .forEach((item) => item.remove());

        imagesList
            .querySelectorAll(".help-text.generated-help-text")
            .forEach((item) => item.remove());

        const allImages = getAllImages();

        // إظهار صندوق الرفع فقط عندما لا توجد صور
        if (uploadBox) {
            uploadBox.style.display =
                allImages.length > 0 ? "none" : "";
        }

        // إظهار صندوق المعاينة عندما توجد صورة واحدة على الأقل
        if (imagesPreviewBox) {
            imagesPreviewBox.style.display =
                allImages.length > 0 ? "block" : "none";
        }

        // إنشاء عناصر الصور
        allImages.forEach((image, index) => {
            const item = createImageItem(image, index);

            if (!item) {
                return;
            }

            imagesList.appendChild(item);
        });

        // إضافة زر المزيد ونص المساعدة مرة واحدة فقط
        if (allImages.length > 0) {
            addHelpText();
            addMiniUpload();
        }

        bindDragSort();
        updateImageNumbers();
    }

    // ============================================================
    // إضافة زر رفع المزيد
    function addMiniUpload() {
    // إضافة عنصر رفع المزيد مرة واحدة فقط
    if (!imagesList || !miniUpload) {
        return;
    }

    const existing =
        imagesList.querySelector(
            ".mini-upload.generated-mini-upload"
        );

    if (existing) {
        return;
    }

    const clone =
        miniUpload.cloneNode(true);

    clone.classList.add(
        "generated-mini-upload"
    );

    const input =
        clone.querySelector("input[type='file']");

    if (input) {
        input.addEventListener("change", () => {
            // إضافة الصور الجديدة من زر إضافة المزيد
            addFiles(input.files);

            input.value = "";
        });
    }

    clone.addEventListener("dragover", (event) => {
        // السماح بإسقاط الصور على زر إضافة المزيد
        event.preventDefault();

        clone.classList.add("drag-over");
    });

    clone.addEventListener("dragleave", () => {
        // إزالة حالة السحب من زر إضافة المزيد
        clone.classList.remove("drag-over");
    });

    clone.addEventListener("drop", (event) => {
        // استقبال الصور المسحوبة إلى زر إضافة المزيد
        event.preventDefault();

        clone.classList.remove("drag-over");

        addFiles(event.dataTransfer.files);
    });

    imagesList.appendChild(clone);
    }

    // ============================================================
    // إضافة نص المساعدة
    function addHelpText() {
        // إضافة نص المساعدة مرة واحدة فقط
        if (!imagesList || !helpText) {
            return;
        }

        const existing =
            imagesList.querySelector(
                ".help-text.generated-help-text"
            );

        if (existing) {
            return;
        }

        const clone =
            helpText.cloneNode(true);

        clone.classList.add(
            "generated-help-text"
        );

        imagesList.appendChild(clone);
    }

    // ============================================================
    // حذف صورة
    function removeImage(item) {
        // حذف الصورة المحددة وتحديث قائمة الصور
        if (!item) {
            return;
        }

        const imageType =
            item.dataset.imageType;

        if (imageType === "existing") {
            const imageId =
                item.dataset.imageId;

            const image =
                existingImages.find(
                    (currentImage) =>
                        String(currentImage.id) ===
                        String(imageId)
                );

            if (image) {
                existingImages =
                    existingImages.filter(
                        (currentImage) =>
                            String(currentImage.id) !==
                            String(imageId)
                    );

                if (!deletedImageIds.includes(imageId)) {
                    deletedImageIds.push(imageId);
                }
            }
        }

        if (imageType === "uploaded") {
            const uploadKey =
                item.dataset.uploadKey;

            uploadedFiles =
                uploadedFiles.filter(
                    (file) =>
                        getFileKey(file) !== uploadKey
                );
        }

        renderImages();
        syncFilesToForm();
    }

    // ============================================================
    // تحديث ترتيب الصور من DOM
    function updateOrderFromDOM() {
        // استخراج ترتيب الصور الحالي من عناصر DOM
        if (!imagesList) {
            return;
        }

        const items =
            imagesList.querySelectorAll(
                ".image-item.generated-image"
            );

        const order = [];

        items.forEach((item) => {
            if (
                item.dataset.imageType ===
                "existing"
            ) {
                order.push({
                    type: "existing",
                    id: item.dataset.imageId
                });

                return;
            }

            if (
                item.dataset.imageType ===
                "uploaded"
            ) {
                order.push({
                    type: "uploaded",
                    key: item.dataset.uploadKey
                });
            }
        });

        if (imagesOrderInput) {
            imagesOrderInput.value =
                JSON.stringify(order);
        }
    }

    // ============================================================
    // تحديث أرقام الصور
    function updateImageNumbers() {
        // تحديث أرقام الصور بعد تغيير ترتيبها
        if (!imagesList) {
            return;
        }

        const items =
            imagesList.querySelectorAll(
                ".image-item.generated-image"
            );

        items.forEach((item, index) => {
            const number =
                item.querySelector(".image-number");

            if (number) {
                number.textContent =
                    index + 1;
            }
        });
    }

    // ============================================================
    // تفعيل السحب والترتيب
    function bindDragSort() {
        // تفعيل سحب الصور وتغيير ترتيبها
        if (!imagesList) {
            return;
        }

        const items =
            imagesList.querySelectorAll(
                ".image-item.generated-image"
            );

        items.forEach((item) => {
            item.addEventListener(
                "dragover",
                (event) => {
                    // تحديد مكان الصورة أثناء السحب
                    event.preventDefault();

                    const dragging =
                        imagesList.querySelector(
                            ".dragging"
                        );

                    if (
                        !dragging ||
                        dragging === item
                    ) {
                        return;
                    }

                    const rect =
                        item.getBoundingClientRect();

                    const offset =
                        event.clientY -
                        rect.top;

                    if (
                        offset >
                        rect.height / 2
                    ) {
                        item.after(dragging);
                    } else {
                        item.before(dragging);
                    }
                }
            );
        });
    }

    // ============================================================
    // استعادة الحالة الأولية
    function resetImages() {
        // إعادة الصور إلى الحالة التي كانت عليها عند تحميل الصفحة
        existingImages =
            initialExistingImages.map(
                (image) => ({
                    ...image
                })
            );

        uploadedFiles = [];

        deletedImageIds = [];

        renderImages();
        syncFilesToForm();
    }

    // ============================================================
    // التحقق قبل إرسال النموذج
    function handleFormSubmit() {
        // مزامنة الصور وترتيبها قبل إرسال النموذج
        syncFilesToForm();
    }

    // ============================================================
    // تهيئة مدير الصور
    function init() {
        // تشغيل جميع وظائف إدارة صور المنتج
        prepareImageTemplate();
        loadInitialImages();
        loadInitialThumbnail();
        initThumbnailUploader();
        initFileUploader();
        renderImages();
        syncFilesToForm();

        const form =
            fileInput?.form ||
            document.querySelector("form");

        if (form) {
            form.addEventListener(
                "submit",
                handleFormSubmit
            );
        }
    }

    // ============================================================
    // تشغيل مدير الصور
    init();

    // ============================================================
    // واجهة عامة 

    window.SimplexImageManager = {
        resetImages,
        resetThumbnail,
        renderImages,
        syncFilesToForm
    };
});

// ================================================================================