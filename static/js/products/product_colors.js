(function () {

    // تهيئة مدير الألوان والمقاسات عند جاهزية الصفحة
    function initColorManager() {

        let form = null;

        const colorsData = [];

        let initialColorsData = [];

        let newColorSizes = [];

        let currentImageFile = null;

        let currentImageURL = null;

        let currentImageName = '';

        let editingIndex = null;


        function getFormFromTarget(target) {
            // الحصول على نموذج المنتج من المعرف أو العنصر نفسه
            if (!target) {
                return null;
            }

            if (typeof target === 'string') {
                return (
                    document.getElementById(target) ||
                    document.querySelector(target)
                );
            }

            return target instanceof HTMLFormElement
                ? target
                : null;
        }


        function handleFormSubmit(event) {
            // منع حفظ المنتج إذا لم تتم إضافة أي ألوان
            syncField();

            if (!colorsData.length) {
                event.preventDefault();
                event.stopImmediatePropagation();

                showToast(
                    'failed-toast',
                    'يرجى اضافة الوان للمنتج اولا!'
                );
            }
        }


        function setForm(target) {
            // ربط مدير الألوان بنموذج المنتج
            const formElement = getFormFromTarget(target);

            if (!formElement) {
                return;
            }

            if (form === formElement) {
                return;
            }

            if (form) {
                form.removeEventListener(
                    'submit',
                    handleFormSubmit
                );
            }

            form = formElement;

            form.addEventListener(
                'submit',
                handleFormSubmit
            );
        }


        function loadInitialColors() {
            // تحميل الألوان الموجودة مسبقاً في صفحة تعديل المنتج
            if (
                window.SimplexInitialColors &&
                Array.isArray(window.SimplexInitialColors)
            ) {
                colorsData.length = 0;

                window.SimplexInitialColors.forEach((c) => {

                    colorsData.push({
                        color: c.color,

                        available: c.available,

                        sizes: c.sizes
                            ? c.sizes.map((s) => ({ ...s }))
                            : [],

                        imageFile: null,

                        imageURL:
                            c.imageURL ||
                            c.image_url ||
                            null,

                        imageName:
                            c.imageName ||
                            c.image_name ||
                            '',

                        isExisting: true,

                        id: c.id || null,
                    });

                });

                initialColorsData = colorsData.map((c) => ({
                    ...c,
                    sizes: c.sizes.map((s) => ({ ...s })),
                }));

                renderColorsList();

                syncField();
            }
        }


        function isEditPage() {
            // التحقق من وجود ألوان محفوظة مسبقاً
            return (
                window.SimplexInitialColors &&
                Array.isArray(window.SimplexInitialColors) &&
                window.SimplexInitialColors.length > 0
            );
        }


        function showForm(show) {
            // إظهار أو إخفاء نموذج اللون
            const newColorForm =
                document.getElementById('new-color-form');

            const addColorBtn =
                document.getElementById('add-color-btn');

            if (!newColorForm || !addColorBtn) {
                return;
            }

            newColorForm.style.display =
                show ? 'block' : 'none';

            addColorBtn.style.display =
                show ? 'none' : 'block';
        }


        function resetForm(title) {
            // إعادة نموذج اللون إلى حالته الافتراضية
            newColorSizes = [];

            currentImageFile = null;

            currentImageURL = null;

            currentImageName = '';

            const colorInput =
                document.getElementById('nc-color');

            const availableInput =
                document.getElementById('nc-available');

            const imageInput =
                document.getElementById('nc-image');

            const sizeInput =
                document.getElementById('nc-size-input');

            const formTitle =
                document.getElementById('form-title-text');


            if (colorInput) {
                colorInput.value = '';
            }

            if (availableInput) {
                availableInput.checked = true;
            }

            if (imageInput) {
                imageInput.value = '';
            }

            if (sizeInput) {
                sizeInput.value = '';
            }

            if (formTitle) {
                formTitle.textContent = title;
            }

            clearErrors();

            setImageUI(null, '');

            renderNewSizes();
        }


        function clearErrors() {
            // إزالة أخطاء نموذج اللون
            const colorInput =
                document.getElementById('nc-color');

            const errColor =
                document.getElementById('err-color');

            const errImage =
                document.getElementById('err-image');


            if (colorInput) {
                colorInput.style.borderColor = '';
            }

            if (errColor) {
                errColor.style.display = 'none';
            }

            if (errImage) {
                errImage.style.display = 'none';
            }
        }


        function setImageUI(url, name) {
            // تحديث واجهة صورة اللون
            const uploadArea =
                document.getElementById('upload-area-wrap');

            const imageWrap =
                document.getElementById('img-selected-wrap');

            const preview =
                document.getElementById('nc-preview');

            const fileName =
                document.getElementById('nc-fname');


            if (url) {

                if (preview) {
                    preview.src = url;
                }

                if (fileName) {
                    fileName.textContent = name;
                }

                if (uploadArea) {
                    uploadArea.style.display = 'none';
                }

                if (imageWrap) {
                    imageWrap.style.display = 'block';
                }

                return;
            }


            if (uploadArea) {
                uploadArea.style.display = 'block';
            }

            if (imageWrap) {
                imageWrap.style.display = 'none';
            }
        }


        function renderNewSizes() {
            // تحديث قائمة المقاسات باستخدام قالب HTML الموجود في الصفحة
            const list =
                document.getElementById('nc-sizes-list');

            const sizeTemplate =
                document.getElementById('new-size-template');

            const emptyTemplate =
                document.getElementById('no-sizes-template');


            if (!list || !sizeTemplate || !emptyTemplate) {
                return;
            }


            list.querySelectorAll('.size-item').forEach(
                (item) => item.remove()
            );

            list.querySelectorAll('.no-sizes').forEach(
                (item) => item.remove()
            );


            if (!newColorSizes.length) {

                const emptyMessage =
                    emptyTemplate.content
                        .firstElementChild
                        .cloneNode(true);

                list.appendChild(emptyMessage);

                return;
            }


            newColorSizes.forEach((size, index) => {

                const item =
                    sizeTemplate.content
                        .firstElementChild
                        .cloneNode(true);

                const name =
                    item.querySelector('.size-name');

                const removeButton =
                    item.querySelector('.remove-size-btn');


                if (name) {
                    name.textContent = size.size;
                }

                if (removeButton) {
                    removeButton.dataset.index = index;
                }


                list.appendChild(item);
            });
        }


        function openNewColorForm() {
            // فتح نموذج إضافة لون جديد
            editingIndex = null;

            resetForm('إضافة لون جديد');

            showForm(true);
        }


        function openEditForm(index) {
            // فتح نموذج تعديل اللون المحدد
            const color = colorsData[index];

            if (!color) {
                return;
            }


            editingIndex = index;

            newColorSizes =
                color.sizes.map((s) => ({ ...s }));

            currentImageFile =
                color.imageFile || null;

            currentImageURL =
                color.imageURL || null;

            currentImageName =
                color.imageName || '';


            const colorInput =
                document.getElementById('nc-color');

            const availableInput =
                document.getElementById('nc-available');

            const sizeInput =
                document.getElementById('nc-size-input');

            const formTitle =
                document.getElementById('form-title-text');


            if (colorInput) {
                colorInput.value = color.color;
            }

            if (availableInput) {
                availableInput.checked = color.available;
            }

            if (sizeInput) {
                sizeInput.value = '';
            }

            if (formTitle) {
                formTitle.textContent = 'تعديل اللون';
            }


            clearErrors();

            setImageUI(
                currentImageURL,
                currentImageName
            );

            renderNewSizes();

            showForm(true);


            setTimeout(() => {

                const newColorForm =
                    document.getElementById('new-color-form');

                if (newColorForm) {
                    newColorForm.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start',
                    });
                }

            }, 50);
        }


        function cancelForm() {
            // إغلاق نموذج إضافة أو تعديل اللون
            showForm(false);
        }


        function resetToLastSavedState() {
            // إعادة الألوان إلى آخر حالة محفوظة
            colorsData.length = 0;

            initialColorsData.forEach((color) => {

                colorsData.push({
                    ...color,
                    sizes: color.sizes.map(
                        (size) => ({ ...size })
                    ),
                });

            });

            renderColorsList();

            syncField();

            cancelForm();
        }


        function resetToEmpty() {
            // حذف جميع الألوان وإعادة القسم لحالته الفارغة
            colorsData.length = 0;

            renderColorsList();

            syncField();

            cancelForm();


            const colorsField =
                document.getElementById('colors_data');

            if (colorsField) {
                colorsField.value = '';
            }
        }


        function resetColors() {
            // إعادة الألوان حسب نوع الصفحة
            if (isEditPage()) {
                resetToLastSavedState();
            } else {
                resetToEmpty();
            }
        }


        function onImageSelected(input) {
            // حفظ الصورة المختارة وعرض المعاينة
            const file = input?.files?.[0];

            if (!file) {
                return;
            }


            currentImageFile = file;

            currentImageURL =
                URL.createObjectURL(file);

            currentImageName =
                file.name;


            setImageUI(
                currentImageURL,
                currentImageName
            );


            const errImage =
                document.getElementById('err-image');

            if (errImage) {
                errImage.style.display = 'none';
            }
        }


        function addSizeToNew() {
            // إضافة مقاس جديد للون الحالي
            const input =
                document.getElementById('nc-size-input');

            const value =
                input?.value.trim();


            if (!value) {
                input?.focus();
                return;
            }


            newColorSizes.push({
                size: value,
            });


            if (input) {
                input.value = '';
            }

            input?.focus();

            renderNewSizes();
        }


        function removeNewSize(index) {
            // حذف المقاس المحدد
            newColorSizes.splice(index, 1);

            renderNewSizes();
        }


        function syncField() {
            // مزامنة بيانات الألوان والصور مع نموذج Django
            const colorsField =
                document.getElementById('colors_data');

            if (!colorsField) {
                return;
            }


            const data = colorsData.map(
                ({
                    imageFile,
                    imageURL,
                    imageName,
                    ...rest
                }) => rest
            );


            colorsField.value =
                JSON.stringify(data);


            document
                .querySelectorAll('.ci-file')
                .forEach((element) => element.remove());


            colorsData.forEach((color, index) => {

                if (!color.imageFile) {
                    return;
                }


                const dataTransfer =
                    new DataTransfer();

                dataTransfer.items.add(
                    color.imageFile
                );


                const input =
                    document.createElement('input');

                input.type = 'file';

                input.name =
                    `color_image_${index}`;

                input.className =
                    'ci-file';

                input.style.display =
                    'none';

                input.files =
                    dataTransfer.files;


                form?.appendChild(input);
            });
        }


        function renderColorsList() {
            // تحديث قائمة الألوان باستخدام قالب HTML الموجود في الصفحة
            const list =
                document.getElementById('colors-list');

            const cardTemplate =
                document.getElementById(
                    'color-card-template'
                );

            const sizeTemplate =
                document.getElementById(
                    'color-size-template'
                );

            const uniformTemplate =
                document.getElementById(
                    'uniform-size-template'
                );


            if (
                !list ||
                !cardTemplate ||
                !sizeTemplate ||
                !uniformTemplate
            ) {
                return;
            }


            list.querySelectorAll('.cv-card').forEach(
                (card) => card.remove()
            );


            colorsData.forEach((color, index) => {

                const card =
                    cardTemplate.content
                        .firstElementChild
                        .cloneNode(true);


                const image =
                    card.querySelector('.cv-image');

                const name =
                    card.querySelector('.cv-name');

                const status =
                    card.querySelector('.cv-status');

                const sizes =
                    card.querySelector('.cv-sizes');

                const editButton =
                    card.querySelector(
                        '[data-action="edit"]'
                    );

                const deleteButton =
                    card.querySelector(
                        '[data-action="delete"]'
                    );


                if (image) {
                    image.src =
                        color.imageURL || '';

                    image.alt =
                        color.color;
                }


                if (name) {
                    name.textContent =
                        color.color;
                }


                if (status) {

                    status.textContent =
                        color.available
                            ? 'متوفر'
                            : 'غير متوفر';

                    status.classList.toggle(
                        'complete',
                        color.available
                    );

                    status.classList.toggle(
                        'cancel',
                        !color.available
                    );
                }


                if (editButton) {
                    editButton.dataset.index =
                        index;
                }


                if (deleteButton) {
                    deleteButton.dataset.index =
                        index;
                }


                if (sizes) {

                    color.sizes.forEach((size) => {

                        const sizeElement =
                            sizeTemplate.content
                                .firstElementChild
                                .cloneNode(true);

                        sizeElement.textContent =
                            size.size;

                        sizes.appendChild(
                            sizeElement
                        );
                    });


                    if (!color.sizes.length) {

                        const uniformSize =
                            uniformTemplate.content
                                .firstElementChild
                                .cloneNode(true);

                        sizes.appendChild(
                            uniformSize
                        );
                    }
                }


                list.appendChild(card);
            });
        }


        function saveColor() {
            // التحقق من اللون وحفظه في قائمة الألوان
            let valid = true;


            const colorInput =
                document.getElementById('nc-color');

            const colorName =
                colorInput?.value.trim();

            const errColor =
                document.getElementById('err-color');

            const errImage =
                document.getElementById('err-image');


            if (!colorName) {

                if (colorInput) {
                    colorInput.style.borderColor =
                        '#e24b4a';
                }

                if (errColor) {
                    errColor.style.display =
                        'block';
                }

                valid = false;

            } else {

                if (colorInput) {
                    colorInput.style.borderColor =
                        '';
                }

                if (errColor) {
                    errColor.style.display =
                        'none';
                }
            }


            if (!currentImageURL) {

                if (errImage) {
                    errImage.style.display =
                        'block';
                }

                valid = false;

            } else {

                if (errImage) {
                    errImage.style.display =
                        'none';
                }
            }


            if (!valid) {
                return;
            }


            const available =
                document.getElementById(
                    'nc-available'
                )?.checked ?? true;


            if (editingIndex !== null) {

                colorsData[editingIndex] = {

                    ...colorsData[editingIndex],

                    color: colorName,

                    available: available,

                    sizes: [...newColorSizes],

                    imageFile:
                        currentImageFile ||
                        colorsData[editingIndex].imageFile,

                    imageURL:
                        currentImageURL ||
                        colorsData[editingIndex].imageURL,

                    imageName:
                        currentImageName ||
                        colorsData[editingIndex].imageName,
                };

            } else {

                colorsData.push({

                    color: colorName,

                    available: available,

                    sizes: [...newColorSizes],

                    imageFile:
                        currentImageFile,

                    imageURL:
                        currentImageURL,

                    imageName:
                        currentImageName,
                });
            }


            cancelForm();

            renderColorsList();

            syncField();
        }


        function deleteColor(index) {
            // حذف اللون المحدد من القائمة
            colorsData.splice(index, 1);

            renderColorsList();

            syncField();
        }


        function handleColorsListClick(event) {
            // التعامل مع أزرار تعديل وحذف الألوان
            const button =
                event.target.closest(
                    'button[data-action]'
                );

            if (!button) {
                return;
            }


            const index =
                Number(button.dataset.index);


            if (Number.isNaN(index)) {
                return;
            }


            if (
                button.dataset.action ===
                'edit'
            ) {

                openEditForm(index);

            } else if (
                button.dataset.action ===
                'delete'
            ) {

                deleteColor(index);
            }
        }


        function handleSizeListClick(event) {
            // التعامل مع زر حذف المقاس
            const button =
                event.target.closest(
                    'button.remove-size-btn'
                );

            if (!button) {
                return;
            }


            const index =
                Number(button.dataset.index);


            if (Number.isNaN(index)) {
                return;
            }


            removeNewSize(index);
        }

        setForm('product_form');

        const ncImage =
            document.getElementById('nc-image');

        if (ncImage) {

            ncImage.addEventListener(
                'change',
                function () {
                    onImageSelected(this);
                }
            );
        }


        const ncColor =
            document.getElementById('nc-color');

        if (ncColor) {

            ncColor.addEventListener(
                'keydown',
                (event) => {

                    if (event.key === 'Enter') {
                        event.preventDefault();
                    }

                }
            );


            ncColor.addEventListener(
                'input',
                function () {

                    if (this.value.trim()) {

                        this.style.borderColor =
                            '';

                        const errColor =
                            document.getElementById(
                                'err-color'
                            );

                        if (errColor) {
                            errColor.style.display =
                                'none';
                        }
                    }

                }
            );
        }


        const ncSizeInput =
            document.getElementById(
                'nc-size-input'
            );

        if (ncSizeInput) {

            ncSizeInput.addEventListener(
                'keydown',
                (event) => {

                    if (event.key === 'Enter') {

                        event.preventDefault();

                        addSizeToNew();
                    }

                }
            );
        }


        const colorsList =
            document.getElementById(
                'colors-list'
            );

        if (colorsList) {

            colorsList.addEventListener(
                'click',
                handleColorsListClick
            );
        }


        const sizesList =
            document.getElementById(
                'nc-sizes-list'
            );

        if (sizesList) {

            sizesList.addEventListener(
                'click',
                handleSizeListClick
            );
        }


        loadInitialColors();


        /*
         * تعريض الدوال للقالب بعد اكتمال التهيئة
         */
        window.SimplexColorManager = {

            setForm,

            openNewColorForm,

            openEditForm,

            cancelForm,

            resetColors,

            onImageSelected,

            addSizeToNew,

            removeNewSize,

            saveColor,

            deleteColor,

        };
    }


    /*
     * تشغيل التهيئة سواء كان الملف قد تم تحميله قبل
     * DOMContentLoaded أو بعده.
     */
    if (document.readyState === 'loading') {

        document.addEventListener(
            'DOMContentLoaded',
            initColorManager,
            { once: true }
        );

    } else {

        initColorManager();

    }

})();