(function () {
    document.addEventListener('DOMContentLoaded', () => {
        let form = null;
        const colorsData = [];
        let initialColorsData = [];
        let newColorSizes = [];
        let currentImageFile = null;
        let currentImageURL = null;
        let currentImageName = '';
        let editingIndex = null;

        function getFormFromTarget(target) {
            if (!target) {
                return null;
            }
            if (typeof target === 'string') {
                return document.getElementById(target) || document.querySelector(target);
            }
            return target instanceof HTMLFormElement ? target : null;
        }

        function handleFormSubmit(event) {
            syncField();
            if (!colorsData || colorsData.length === 0) {
                event.preventDefault();
                showToast('failed-toast', 'يرجى اضافة الوان للمنتج اولا!');
            }
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
                form.removeEventListener('submit', handleFormSubmit);
            }
            form = formElement;
            form.addEventListener('submit', handleFormSubmit);
        }

        // Default form lookup for the current product add page.
        setForm('add_product_form');

        function loadInitialColors() {
            if (window.SimplexInitialColors && Array.isArray(window.SimplexInitialColors)) {
                colorsData.length = 0;
                window.SimplexInitialColors.forEach((c) => {
                    colorsData.push({
                        color: c.color,
                        available: c.available,
                        sizes: c.sizes ? c.sizes.map((s) => ({ ...s })) : [],
                        imageFile: null,
                        imageURL: c.imageURL || c.image_url || null,
                        imageName: c.imageName || c.image_name || '',
                        isExisting: true,
                        id: c.id || null,
                    });
                });
                // Save initial state for reset on edit page
                initialColorsData = colorsData.map((c) => ({ ...c, sizes: c.sizes.map((s) => ({ ...s })) }));
                renderColorsList();
                syncField();
            }
        }

        function isEditPage() {
            return window.SimplexInitialColors && Array.isArray(window.SimplexInitialColors) && window.SimplexInitialColors.length > 0;
        }

        function showForm(show) {
            const newColorForm = document.getElementById('new-color-form');
            const addColorBtn = document.getElementById('add-color-btn');
            if (!newColorForm || !addColorBtn) {
                return;
            }
            newColorForm.style.display = show ? 'block' : 'none';
            addColorBtn.style.display = show ? 'none' : 'block';
        }

        function resetForm(title) {
            newColorSizes = [];
            currentImageFile = null;
            currentImageURL = null;
            currentImageName = '';
            const nfColor = document.getElementById('nc-color');
            const nfAvailable = document.getElementById('nc-available');
            const nfImage = document.getElementById('nc-image');
            const nfSizeInput = document.getElementById('nc-size-input');
            const formTitle = document.getElementById('form-title-text');

            if (nfColor) nfColor.value = '';
            if (nfAvailable) nfAvailable.checked = true;
            if (nfImage) nfImage.value = '';
            if (nfSizeInput) nfSizeInput.value = '';
            if (formTitle) formTitle.textContent = title;

            clearErrors();
            setImageUI(null, '');
            renderNewSizes();
        }

        function clearErrors() {
            const colorInput = document.getElementById('nc-color');
            const errColor = document.getElementById('err-color');
            const errImage = document.getElementById('err-image');

            if (colorInput) colorInput.style.borderColor = '#ddd';
            if (errColor) errColor.style.display = 'none';
            if (errImage) errImage.style.display = 'none';
        }

        function setImageUI(url, name) {
            const uploadArea = document.getElementById('upload-area-wrap');
            const imgWrap = document.getElementById('img-selected-wrap');
            const preview = document.getElementById('nc-preview');
            const fname = document.getElementById('nc-fname');

            if (url) {
                if (preview) preview.src = url;
                if (fname) fname.textContent = name;
                if (uploadArea) uploadArea.style.display = 'none';
                if (imgWrap) imgWrap.style.display = 'block';
                return;
            }

            if (uploadArea) uploadArea.style.display = 'block';
            if (imgWrap) imgWrap.style.display = 'none';
        }

        function renderNewSizes() {
            const el = document.getElementById('nc-sizes-list');
            if (!el) {
                return;
            }

            if (!newColorSizes.length) {
                el.innerHTML = '<p style="font-size:12px; color:#aaa; margin:0 0 8px;">لم تضف مقاسات — سيُضاف مقاس موحد تلقائياً</p>';
                return;
            }

            el.innerHTML = newColorSizes.map((s, i) => `
                <div class="nc-size-item">
                    <span style="font-size:13px; font-weight:600; flex:1;">${s.size}</span>
                    <button type="button" class="remove-size-btn" data-index="${i}"
                            style="background:none; border:none; color:#bbb; cursor:pointer; font-size:16px; padding:0 2px; line-height:1;">✕</button>
                </div>`).join('');
        }

        function openNewColorForm() {
            editingIndex = null;
            resetForm('إضافة لون جديد');
            showForm(true);
        }

        function openEditForm(index) {
            const c = colorsData[index];
            if (!c) {
                return;
            }

            editingIndex = index;
            newColorSizes = c.sizes.map((s) => ({ ...s }));
            currentImageFile = c.imageFile || null;
            currentImageURL = c.imageURL || null;
            currentImageName = c.imageName || '';

            const colorInput = document.getElementById('nc-color');
            const availableInput = document.getElementById('nc-available');
            const sizeInput = document.getElementById('nc-size-input');
            const formTitle = document.getElementById('form-title-text');

            if (colorInput) colorInput.value = c.color;
            if (availableInput) availableInput.checked = c.available;
            if (sizeInput) sizeInput.value = '';
            if (formTitle) formTitle.textContent = 'تعديل اللون';

            clearErrors();
            setImageUI(currentImageURL, currentImageName);
            renderNewSizes();
            showForm(true);

            setTimeout(() => {
                const newColorForm = document.getElementById('new-color-form');
                if (newColorForm) {
                    newColorForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 50);
        }

        function cancelForm() {
            showForm(false);
        }

        function resetToLastSavedState() {
            colorsData.length = 0;
            initialColorsData.forEach((c) => {
                colorsData.push({ ...c, sizes: c.sizes.map((s) => ({ ...s })) });
            });
            renderColorsList();
            syncField();
            cancelForm();
        }

        function resetToEmpty() {
            colorsData.length = 0;
            renderColorsList();
            syncField();
            cancelForm();
            const colorsField = document.getElementById('colors_data');
            if (colorsField) {
                colorsField.value = '';
            }
        }

        function resetColors() {
            if (isEditPage()) {
                resetToLastSavedState();
            } else {
                resetToEmpty();
            }
        }

        function onImageSelected(input) {
            const file = input?.files?.[0];
            if (!file) {
                return;
            }

            currentImageFile = file;
            currentImageURL = URL.createObjectURL(file);
            currentImageName = file.name;
            setImageUI(currentImageURL, currentImageName);

            const errImage = document.getElementById('err-image');
            if (errImage) errImage.style.display = 'none';
        }

        function addSizeToNew() {
            const inp = document.getElementById('nc-size-input');
            const val = inp?.value.trim();
            if (!val) {
                inp?.focus();
                return;
            }

            newColorSizes.push({
                size: val,
            });

            if (inp) inp.value = '';
            inp?.focus();
            renderNewSizes();
        }

        function removeNewSize(i) {
            newColorSizes.splice(i, 1);
            renderNewSizes();
        }

        function syncField() {
            const colorsField = document.getElementById('colors_data');
            if (!colorsField) {
                return;
            }

            const data = colorsData.map(({ imageFile, imageURL, imageName, ...rest }) => rest);
            colorsField.value = JSON.stringify(data);

            document.querySelectorAll('.ci-file').forEach((el) => el.remove());

            colorsData.forEach((c, i) => {
                if (!c.imageFile) {
                    return;
                }
                const dt = new DataTransfer();
                dt.items.add(c.imageFile);
                const inp = document.createElement('input');
                inp.type = 'file';
                inp.name = `color_image_${i}`;
                inp.className = 'ci-file';
                inp.style.display = 'none';
                inp.files = dt.files;
                form?.appendChild(inp);
            });
        }

        function renderColorsList() {
            const el = document.getElementById('colors-list');
            if (!el) {
                return;
            }

            el.innerHTML = colorsData
                .map((c, i) => `
                    <div class="cv-card">
                        <div class="cv-header">
                            <img src="${c.imageURL}" alt="${c.color}"
                                style="width:34px; height:34px; border-radius:50%; object-fit:cover; border:1px solid #ddd; flex-shrink:0;">
                            <span>${c.color}</span>
                            <span class="cv-badge ${c.available ? 'cv-yes' : 'cv-no'}">
                                ${c.available ? 'متوفر' : 'غير متوفر'}
                            </span>
                        </div>
                        <div style="font-size:13px; font-weight:600; color:#555; margin-bottom:6px;">المقاسات:</div>
                        <div class="cv-sizes">
                            ${c.sizes.length
                                ? c.sizes.map((s) => `<span class="cv-chip ">${s.size}</span>`).join('')
                                : '<span style="color:#aaa; font-size:13px;">مقاس موحد</span>'}
                        </div>
                        <div class="cv-actions">
                            <button type="button" class="btn-cv-edit" data-action="edit" data-index="${i}">تعديل</button>
                            <button type="button" class="btn-cv-del" data-action="delete" data-index="${i}">حذف</button>
                        </div>
                    </div>`)
                .join('');
        }

        function saveColor() {
            let valid = true;
            const colorInput = document.getElementById('nc-color');
            const colorName = colorInput?.value.trim();
            const errColor = document.getElementById('err-color');
            const errImage = document.getElementById('err-image');

            if (!colorName) {
                if (colorInput) colorInput.style.borderColor = '#e24b4a';
                if (errColor) errColor.style.display = 'block';
                valid = false;
            } else {
                if (colorInput) colorInput.style.borderColor = '#ddd';
                if (errColor) errColor.style.display = 'none';
            }

            if (!currentImageURL) {
                if (errImage) errImage.style.display = 'block';
                valid = false;
            } else {
                if (errImage) errImage.style.display = 'none';
            }

            if (!valid) {
                return;
            }

            const entry = {
                color: colorName,
                available: document.getElementById('nc-available')?.checked ?? true,
                sizes: [...newColorSizes],
                imageFile: currentImageFile,
                imageURL: currentImageURL,
                imageName: currentImageName,
            };

            if (editingIndex !== null) {
                // Keep original data and only update changed fields
                colorsData[editingIndex] = {
                    ...colorsData[editingIndex],  // Preserve id and other original fields
                    color: colorName,
                    available: document.getElementById('nc-available')?.checked ?? true,
                    sizes: [...newColorSizes],
                    // Only update image if a new one was selected
                    imageFile: currentImageFile || colorsData[editingIndex].imageFile,
                    imageURL: currentImageURL || colorsData[editingIndex].imageURL,
                    imageName: currentImageName || colorsData[editingIndex].imageName,
                };
            } else {
                colorsData.push(entry);
            }

            cancelForm();
            renderColorsList();
            syncField();
        }

        function deleteColor(i) {
            colorsData.splice(i, 1);
            renderColorsList();
            syncField();
        }

        function handleColorsListClick(event) {
            const button = event.target.closest('button[data-action]');
            if (!button) {
                return;
            }
            const index = Number(button.dataset.index);
            if (Number.isNaN(index)) {
                return;
            }

            if (button.dataset.action === 'edit') {
                openEditForm(index);
            } else if (button.dataset.action === 'delete') {
                deleteColor(index);
            }
        }

        function handleSizeListClick(event) {
            const button = event.target.closest('button.remove-size-btn');
            if (!button) {
                return;
            }
            const index = Number(button.dataset.index);
            if (Number.isNaN(index)) {
                return;
            }

            removeNewSize(index);
        }

        if (form) {
            form.addEventListener('submit', (event) => {
                syncField();
                if (!colorsData || colorsData.length === 0) {
                    event.preventDefault();
                    showToast('failed-toast', 'يرجى اضافة الوان للمنتج اولا!');
                }
            });
        }

        const ncImage = document.getElementById('nc-image');
        if (ncImage) {
            ncImage.addEventListener('change', function () {
                onImageSelected(this);
            });
        }

        const ncColor = document.getElementById('nc-color');
        if (ncColor) {
            ncColor.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                }
            });
            ncColor.addEventListener('input', function () {
                if (this.value.trim()) {
                    this.style.borderColor = '#ddd';
                    const errColor = document.getElementById('err-color');
                    if (errColor) errColor.style.display = 'none';
                }
            });
        }

        const ncSizeInput = document.getElementById('nc-size-input');
        if (ncSizeInput) {
            ncSizeInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    addSizeToNew();
                }
            });
        }

        const colorsList = document.getElementById('colors-list');
        if (colorsList) {
            colorsList.addEventListener('click', handleColorsListClick);
        }

        const sizesList = document.getElementById('nc-sizes-list');
        if (sizesList) {
            sizesList.addEventListener('click', handleSizeListClick);
        }

        // Load initial colors for edit page
        loadInitialColors();

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
    });
})();
