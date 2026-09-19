// إعداد نماذج تعديل الخصم وحالة الفاتورة
function setupInvoiceEditForms() {

    const forms = [
        document.getElementById("invoice_discount_form"),
        document.getElementById("invoice_status_form")
    ].filter(Boolean);

    if (!forms.length) {
        return;
    }

    forms.forEach(form => {

        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            // إزالة حالة الخطأ السابقة
            form.querySelectorAll(".field").forEach(field => {
                field.classList.remove("has-error");

                const errorElement = field.querySelector(".js-error");

                if (errorElement) {
                    errorElement.classList.remove("js-error");
                }
            });

            const formData = new FormData(form);
            const saveButton = form.querySelector(".save-btn");

            if (saveButton) {
                saveButton.disabled = true;
            }

            try {

                const response = await fetch(form.action, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                const data = await response.json();

                // =====================================================
                // يوجد خطأ
                // =====================================================

                if (!response.ok || !data.success) {

                    if (data.errors) {

                        Object.entries(data.errors).forEach(
                            ([fieldName, message]) => {

                                const input = form.querySelector(
                                    `[name="${fieldName}"]`
                                );

                                if (!input) {
                                    return;
                                }

                                const field = input.closest(".field");

                                if (!field) {
                                    return;
                                }

                                field.classList.add("has-error");

                                // البحث عن help-text الموجود أصلًا
                                const helpText =
                                    field.querySelector(".help-text");

                                if (helpText) {

                                    // استبدال النص الأصلي برسالة الخطأ
                                    helpText.textContent = message;

                                    // تمييزه كرسالة خطأ
                                    helpText.classList.add("js-error");

                                } else {

                                    // إنشاء help-text في حال عدم وجوده
                                    const errorElement =
                                        document.createElement("span");

                                    errorElement.className =
                                        "help-text js-error";

                                    errorElement.textContent = message;

                                    input.closest(
                                        ".input, .select-control"
                                    )?.insertAdjacentElement(
                                        "afterend",
                                        errorElement
                                    );
                                }
                            }
                        );
                    }

                    // عرض رسالة الخطأ
                    showToast(
                        "failed-toast",
                        data.message || "يرجى تصحيح الأخطاء الموجودة."
                    );

                    return;
                }

                // =====================================================
                // نجاح التعديل
                // =====================================================

                showToast(
                    "success-toast",
                    data.message || "تم التعديل بنجاح"
                );

                // إعادة تحميل الصفحة بعد ظهور رسالة النجاح
                setTimeout(() => {
                    location.reload();
                }, 800);

            } catch (error) {

                console.error(
                    "حدث خطأ أثناء تعديل الفاتورة:",
                    error
                );

                showToast(
                    "failed-toast",
                    "حدث خطأ أثناء تعديل الفاتورة."
                );

            } finally {

                if (saveButton) {
                    saveButton.disabled = false;
                }
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    setupInvoiceEditForms();
});
// ======================================================
// دالة خاصة بفورم تعديل الخصم بالفاتورة تحسب القيمة بعد الخصم تلقائيا وفقا لقيمة الاصلية والخصم المكتوب مباشرة
function initDiscountCalculation() {
    const form = document.getElementById('invoice_discount_form');
    if (!form) return; // الفورم غير موجود في الصفحة

    const originalValueEl = document.getElementById('original-value');
    const afterDiscountBox = document.getElementById('after-discount-box');
    const afterDiscountValueEl = document.getElementById('after-discount-value');
    const discountInput = document.getElementById('discount-input');

    // استخراج القيمة الأصلية كرقم (تجاهل نص currency)
    function getOriginalValue() {
        const rawText = originalValueEl.firstChild.textContent;
        return parseFloat(rawText.trim());
    }

    const originalValue = getOriginalValue();

    function updateAfterDiscount() {
        const raw = discountInput.value;
        const discount = parseFloat(raw);

        if (raw === '' || isNaN(discount)) {
            afterDiscountValueEl.firstChild.textContent = '--- ';
            afterDiscountBox.classList.remove('after-discount');
            return;
        }

        let result = originalValue - discount;

        // منع القيمة من أن تصبح سالبة
        if (result < 0) {
            result = 0;
        }

        afterDiscountValueEl.firstChild.textContent = result.toFixed(2) + ' ';
        afterDiscountBox.classList.add('after-discount');
    }

    discountInput.addEventListener('input', updateAfterDiscount);
    // إعادة الحساب بعد الضغط على إعادة التعيين
    form.addEventListener('reset', function () {
        setTimeout(() => {
            updateAfterDiscount();
        }, 0);
    });
}

document.addEventListener('DOMContentLoaded', initDiscountCalculation);
// ======================================================
