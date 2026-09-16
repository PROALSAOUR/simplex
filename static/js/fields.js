// ======================================================
// منع كتابة قيمة اكبر من الحد الاقصى داخل حقول الاعداد كما تمنع ايضا كتابة الحروف
function limitNumberInputs() {

    document.querySelectorAll('input[inputmode="decimal"][max]').forEach(input => {

        input.addEventListener('input', function () {

            // السماح بالأرقام ونقطة عشرية واحدة فقط
            this.value = this.value
                .replace(/[^\d.]/g, '')
                .replace(/(\..*)\./g, '$1');

            const max = Number(this.max);
            const value = Number(this.value);

            if (
                this.value !== '' &&
                !Number.isNaN(max) &&
                value > max
            ) {
                this.value = max;
            }

        });

    });

}
limitNumberInputs();
// ======================================================
// عداد الحروف داخل التسكست اريا
function initTextareaCounters() {
    // البحث عن كل التيكست اريا الموجودة بالصفحة
    const textareas = document.querySelectorAll('textarea[maxlength]');

    textareas.forEach(textarea => {
        // البحث عن الـ counter المرتبط بهذا التيكست اريا (داخل نفس الحاوية الأب)
        const wrapper = textarea.closest('.input') || textarea.parentElement;
        const counter = wrapper ? wrapper.querySelector('.counter') : null;

        if (!counter) return; // لو مفيش counter نتجاهل هذا العنصر

        const currentSpan = counter.querySelector('.current-c');
        const maxSpan = counter.querySelector('.max-c');

        const maxLength = textarea.getAttribute('maxlength');

        // وضع القيمة القصوى داخل max-c عند التحميل
        if (maxSpan) {
            maxSpan.textContent = maxLength;
        }

        // عرض القيمة الحالية عند التحميل (بدون إضافة أي كلاس)
        if (currentSpan) {
            currentSpan.textContent = textarea.value.length;
        }

        // دالة تحديث العداد والكلاسات (تعمل فقط أثناء الكتابة)
        function updateCounter() {
            const currentLength = textarea.value.length;

            if (currentSpan) {
                currentSpan.textContent = currentLength;
            }

            // إزالة الكلاسين أولاً لتفادي التكرار
            counter.classList.remove('complete', 'cancel');

            if (currentLength > parseInt(maxLength, 10)) {
                counter.classList.add('cancel');
            } else {
                counter.classList.add('complete');
            }
        }

        // تحديث القيمة والكلاس فقط عند الكتابة (input event)
        textarea.addEventListener('input', updateCounter);

    });
}

// تشغيل الدالة بعد تحميل الصفحة
document.addEventListener('DOMContentLoaded', initTextareaCounters);

// ==========================================================
// دوال بناء قائمة خيارات سليكت تلقائياً لنتمكن من تنسيقها كما نشاء
/*
  يبحث عن كل عنصر بالكلاس js-custom-select،
  يأخذ الـ select الموجود بداخله (يدوي أو مُولَّد من Django Forms)،
  يبني فوقه واجهة مخصصة من نفس الـ options بالضبط، ثم يخفي الأصلي.
  لا داعي لكتابة أي خيار مرتين، ولا حاجة لتعديل السكربت عند تغيير الخيارات.
*/
(function () {
    function buildCustomSelect(container) {
        const nativeSel = container.querySelector('select');
        if (!nativeSel) return;
 
        nativeSel.style.display = 'none';
 
        const wrapper = document.createElement('div');
        wrapper.className = 'custom-select';
        if (nativeSel.disabled) wrapper.classList.add('disabled');
 
        const trigger = document.createElement('div');
        trigger.className = 'select-trigger';
        trigger.tabIndex = 0;
        trigger.setAttribute('role', 'combobox');
        trigger.setAttribute('aria-haspopup', 'listbox');
        trigger.setAttribute('aria-expanded', 'false');
        if (nativeSel.id) trigger.id = nativeSel.id + '-trigger';
 
        const valueLabel = document.createElement('span');
        valueLabel.className = 'select-value';
 
        const icon = document.createElement('i');
        icon.className = 'fa-solid fa-chevron-down';
 
        trigger.appendChild(valueLabel);
        trigger.appendChild(icon);
 
        const panel = document.createElement('div');
        panel.className = 'select-panel';
        panel.setAttribute('role', 'listbox');
 
        const optionEls = [];
        Array.from(nativeSel.options).forEach(function (opt) {
            const optDiv = document.createElement('div');
            optDiv.className = 'select-option';
            optDiv.textContent = opt.textContent.trim();
            optDiv.dataset.value = opt.value;
 
            if (opt.value === '') optDiv.classList.add('placeholder');
            if (opt.disabled) optDiv.setAttribute('aria-disabled', 'true');
            if (opt.selected) optDiv.classList.add('selected');
 
            optDiv.addEventListener('click', function () {
                if (opt.disabled) return;
 
                nativeSel.value = opt.value;
                nativeSel.dispatchEvent(new Event('change', { bubbles: true }));
 
                valueLabel.textContent = optDiv.textContent;
                wrapper.classList.toggle('has-value', opt.value !== '');
 
                optionEls.forEach(function (o) { o.classList.remove('selected'); });
                optDiv.classList.add('selected');
 
                closePanel();
            });
 
            panel.appendChild(optDiv);
            optionEls.push(optDiv);
        });
 
        const initiallySelected = nativeSel.options[nativeSel.selectedIndex];
        valueLabel.textContent = initiallySelected ? initiallySelected.textContent.trim() : '';
        if (nativeSel.value !== '') wrapper.classList.add('has-value');
 
        wrapper.appendChild(trigger);
        wrapper.appendChild(panel);
        container.insertBefore(wrapper, nativeSel);
        container.appendChild(nativeSel); // يبقى بالـ DOM (مخفي فقط) لأجل الفورم
 
        function openPanel() {
            wrapper.classList.add('open');
            trigger.setAttribute('aria-expanded', 'true');
        }
        function closePanel() {
            wrapper.classList.remove('open');
            trigger.setAttribute('aria-expanded', 'false');
        }
 
        trigger.addEventListener('click', function () {
            if (nativeSel.disabled) return;
            wrapper.classList.contains('open') ? closePanel() : openPanel();
        });
 
        trigger.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                wrapper.classList.contains('open') ? closePanel() : openPanel();
            }
            if (e.key === 'Escape') closePanel();
        });
 
        document.addEventListener('click', function (e) {
            if (!wrapper.contains(e.target)) closePanel();
        });
    }
 
    document.querySelectorAll('.js-custom-select').forEach(buildCustomSelect);
})();

// ==========================================================
// إزالة حالة الخطأ من الحقول عند تغيير القيمة الخاطئة، بحيث لا تبقى حالة الخطأ بعد أن يقوم المستخدم بتصحيح القيمة.
document.querySelectorAll('.field.has-error .input').forEach(input => {
    input.addEventListener('input', function () {
        const wrapper = this.closest('.field'); 
        wrapper.classList.remove('has-error');
    }); 
});
// ==========================================================
// دالة تقوم بالانتقال إلى أول حقل يحتوي على خطأ عند تحميل الصفحة التي بها اخطاء بالحقول الفورم، بحيث يسهل على المستخدم معرفة مكان الخطأ مباشرة.
function scrollToFirstError() { 
    const firstError = document.querySelector('.field.has-error'); 
    if (!firstError) { 
        return;
    } 
    const headerHeight = parseInt( getComputedStyle(document.documentElement) .getPropertyValue('--header-height') ) || 75; 
    const top = firstError.getBoundingClientRect().top + window.scrollY - headerHeight - 10; 
    window.scrollTo({ top: top, behavior: 'smooth' }); 
} 
window.addEventListener('load', scrollToFirstError);
// ==========================================================
// دوال التحكم بازرار النقصان والزيادة الخاصة بالكمية
function changeQuantity(button, amount) {
    /* تغيير كمية المنتج مع الالتزام بالحد الأدنى والأقصى */
    const container = button.closest(".qty-control");

    if (!container) return;

    const input = container.querySelector(".qty-input");

    if (!input) return;

    let value = parseInt(input.value, 10);

    if (Number.isNaN(value)) {
        value = 1;
    }

    const min = 1;
    const max = parseInt(input.max, 10);

    value += amount;

    value = Math.max(value, min);

    if (!Number.isNaN(max)) {
        value = Math.min(value, max);
    }

    input.value = value;
}
// ==========================================================

