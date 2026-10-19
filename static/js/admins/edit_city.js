document.addEventListener("DOMContentLoaded", () => {

    // تهيئة نموذج تعديل بيانات المدينة
    const form = document.getElementById("city_form");

    if (!form) return;

    // حفظ القيم الأصلية لإعادة التعيين
    const originalValues = new FormData(form);

    /*
     * إزالة أخطاء الحقول
     */
    function clearFieldErrors() {

        form.querySelectorAll(".field.has-error").forEach(field => {
            field.classList.remove("has-error");
        });

        form.querySelectorAll(".field .js-error").forEach(error => {
            error.remove();
        });
    }

    /*
     * عرض أخطاء التحقق بجانب الحقول
     */
    function showFieldErrors(errors) {

        Object.entries(errors || {}).forEach(([fieldName, messages]) => {

            const field = form.querySelector(`[name="${fieldName}"]`);

            if (!field) return;

            const fieldContainer = field.closest(".field");

            if (!fieldContainer) return;

            fieldContainer.classList.add("has-error");

            // البحث عن نص المساعدة الموجود مسبقًا
            let helpText = fieldContainer.querySelector(".help-text");

            // إنشاء عنصر لرسالة الخطأ إذا لم يكن موجودًا
            if (!helpText) {
                helpText = document.createElement("span");
                helpText.className = "help-text";
                fieldContainer.appendChild(helpText);
            }

            // استبدال نص المساعدة برسالة الخطأ
            helpText.textContent = messages.join(" ");
        });
    }

    /*
     * إرسال النموذج وحفظ تعديلات المدينة
     */
    form.addEventListener("submit", async event => {

        event.preventDefault();

        clearFieldErrors();

        const formData = new FormData(form);

        try {

            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            const data = await response.json();

            if (data.status === "success") {

                showToast(
                    "success-toast",
                    data.message || "تم حفظ التعديلات  بنجاح"
                );

                if (form.dataset.redirectUrl) {
                    setTimeout(() => {
                        window.location.href = form.dataset.redirectUrl;
                    }, 500);
                    return;
                }

                setTimeout(() => {
                    window.location.reload();
                }, 500);

                return;
            }

            if (data.status === "error") {

                showFieldErrors(data.errors);

                showToast(
                    "failed-toast",
                    "يرجى التحقق من البيانات المدخلة"
                );

                return;
            }

            showToast(
                "failed-toast",
                "تعذر حفظ التعديلات "
            );

        } catch (error) {

            console.error("Edit city error:", error);

            showToast(
                "failed-toast",
                "حدث خطأ أثناء حفظ التعديلات "
            );
        }
    });

    /*
     * إزالة أخطاء الحقول عند تعديل قيمها
     */
    form.addEventListener("input", event => {

        const fieldContainer = event.target.closest(".field");

        if (!fieldContainer) return;

        fieldContainer.classList.remove("has-error");

        fieldContainer.querySelectorAll(".js-error").forEach(error => {
            error.remove();
        });
    });

    /*
     * إعادة تعيين النموذج إلى القيم الأصلية
     */
    form.addEventListener("reset", () => {

        clearFieldErrors();

        setTimeout(() => {

            // تحديث عناصر النموذج بعد إعادة التعيين
            form.querySelectorAll("select").forEach(select => {
                select.dispatchEvent(
                    new Event("change", { bubbles: true })
                );
            });

        }, 0);
    });

});