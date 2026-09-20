// التحقق من حقول الفورم عبر اجاكس لمنع فقدان بيانات الفورم والصور والمتغيرات
document.addEventListener("DOMContentLoaded", function () {
    // إرسال نموذج المنتج عبر AJAX لمنع إعادة تحميل الصفحة وفقدان الملفات
    const form = document.getElementById("product_form");
    let submitting = false;
    
    if (!form) {
        return;
    }
    
    // زر اعادة التعيين الخاص بالفورم 
    const resetButton = form.querySelector('button[type="reset"].reset');
    if (resetButton) {
        resetButton.addEventListener("click", function () {
            // إعادة جميع حقول النموذج والصور والألوان إلى حالتها الأصلية
            form.reset();

            if (window.SimplexImageManager) {
                window.SimplexImageManager.resetImages();
                window.SimplexImageManager.resetThumbnail();
            }

            if (window.SimplexColorManager) {
                window.SimplexColorManager.resetColors();
            }
        });
    }

    form.addEventListener("submit", async function (event) {
        // اعتراض الإرسال التقليدي وإرسال FormData عبر fetch
        event.preventDefault();

        if (submitting) {
            return;
        }

        // مزامنة الصور قبل إنشاء FormData
        if (window.SimplexImageManager) {
            window.SimplexImageManager.syncFilesToForm();
        }

        // مزامنة الألوان وملفات صور الألوان
        if (window.SimplexColorManager) {
            const saveButton = document.activeElement;

            if (
                saveButton &&
                saveButton.type === "submit"
            ) {
                const colorsField =
                    document.getElementById("colors_data");

                if (
                    colorsField &&
                    !colorsField.value.trim()
                ) {
                    showToast(
                        "failed-toast",
                        "يرجى إضافة ألوان للمنتج أولاً!"
                    );

                    return;
                }
            }
        }

        submitting = true;

        const submitButton =
            form.querySelector(
                'button[type="submit"], input[type="submit"]'
            );

        const originalButtonText =
            submitButton?.textContent;

        if (submitButton) {
            submitButton.disabled = true;

            if (submitButton.tagName === "BUTTON") {
                submitButton.textContent = "جاري الحفظ...";
            }
        }

        try {
            const formData = new FormData(form);

            const response = await fetch(
                form.action || window.location.href,
                {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With":
                            "XMLHttpRequest",
                    },
                }
            );

            const data = await response.json();

            if (data.success) {
                showToast(
                    "success-toast",
                    data.message || "تمت إضافة المنتج بنجاح"
                );

                if (data.redirect_url) {
                    setTimeout(function () {
                        // الانتقال بعد نجاح حفظ المنتج
                        window.location.href =
                            data.redirect_url;
                    }, 500);
                }

                return;
            }
            
            if (
                data.non_field_errors &&
                data.non_field_errors.length
            ) {
                data.non_field_errors.forEach(function (error) {
                    // عرض الخطأ العام للنموذج
                    if (error.message) {
                        showToast(
                            "failed-toast",
                            error.message
                        );
                    }
                });
            }
            
            showFormErrors( form, data.errors || {}, data.non_field_errors || [] ); 
            openDetailsWithErrors();
            scrollToFirstError();
            showToast(
                "failed-toast",
                "يرجى تصحيح الأخطاء الموجودة في النموذج."
            );

        } catch (error) {
            
            showToast(
                "failed-toast",
                "حدث خطأ أثناء حفظ المنتج، يرجى المحاولة مرة أخرى."
            );

        } finally {
            submitting = false;

            if (submitButton) {
                submitButton.disabled = false;

                if (
                    submitButton.tagName === "BUTTON" &&
                    originalButtonText !== undefined
                ) {
                    submitButton.textContent =
                        originalButtonText;
                }
            }
        }
    });


    function clearFormErrors(form) {
        // إزالة حالة الخطأ وإعادة نصوص المساعدة إلى محتواها الأصلي
        form.querySelectorAll(".field.has-error").forEach((field) => {
            field.classList.remove("has-error");
        });

        form.querySelectorAll(".help-text").forEach((helpText) => {
            if (helpText.dataset.originalText !== undefined) {
                helpText.textContent = helpText.dataset.originalText;
            }
        });
    }


    function showFormErrors(form, errors, nonFieldErrors = []) {
        // إضافة has-error وعرض رسالة الخطأ داخل نص المساعدة الموجود
        clearFormErrors(form);

        Object.entries(errors || {}).forEach(
            ([fieldName, messages]) => {
                const input = form.querySelector(
                    `[name="${CSS.escape(fieldName)}"]`
                );

                if (!input) {
                    return;
                }

                const field =
                    input.closest(".field");

                if (!field) {
                    return;
                }

                field.classList.add("has-error");

                const helpText =
                    field.querySelector(".help-text");

                if (!helpText) {
                    return;
                }

                if (
                    helpText.dataset.originalText ===
                    undefined
                ) {
                    helpText.dataset.originalText =
                        helpText.textContent;
                }

                const errorMessages = messages.map(
                    (error) => {
                        // استخراج نص الخطأ سواء كان كائنًا أو نصًا
                        if (
                            typeof error === "object" &&
                            error !== null
                        ) {
                            return error.message || "";
                        }

                        return error;
                    }
                );

                helpText.textContent =
                    errorMessages.join(" ");
            }
        );

        if (nonFieldErrors.length) {
            const firstField =
                form.querySelector(".field");

            const helpText =
                firstField?.querySelector(".help-text");

            if (helpText) {
                if (
                    helpText.dataset.originalText ===
                    undefined
                ) {
                    helpText.dataset.originalText =
                        helpText.textContent;
                }

                const errorMessages =
                    nonFieldErrors.map(
                        (error) => {
                            // استخراج نص الخطأ العام سواء كان كائنًا أو نصًا
                            if (
                                typeof error === "object" &&
                                error !== null
                            ) {
                                return error.message || "";
                            }

                            return error;
                        }
                    );

                helpText.textContent =
                    errorMessages.join(" ");
            }
        }
    }
});
// ================================================================
// التحكم بظهور/إخفاء حقل سبب الرفض وفقا لحالة المنتج
function setupRejectedCause() {
    // إظهار سبب الرفض فقط عندما تكون حالة المنتج "مرفوض"
    const status = document.getElementById("id_status");
    const rejectedCause = document.getElementById("rejected_cause");

    if (!status || !rejectedCause) return;

    const rejectedCauseField = rejectedCause.closest(".field");
    const form = status.closest("form");

    function updateRejectedCause() {
        // إظهار الحقل عند اختيار حالة الرفض وإخفاؤه في غير ذلك
        const isRejected = status.value === "rejected";

        rejectedCauseField.style.display = isRejected ? "" : "none";
        rejectedCause.required = isRejected;
    }
    // تحديث الحقل مباشرة عند تغيير الحالة
    status.addEventListener("change", updateRejectedCause);

    // إعادة تحديث الحقل بعد إعادة ضبط النموذج
    if (form) {
        form.addEventListener("reset", function () {
            // انتظار انتهاء reset ثم قراءة القيمة الجديدة للحالة
            setTimeout(updateRejectedCause, 0);
        });
    }
    // تطبيق الحالة عند تحميل الصفحة
    updateRejectedCause();
}

document.addEventListener("DOMContentLoaded", setupRejectedCause);
// ================================================================================
