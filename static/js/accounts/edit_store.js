document.addEventListener("DOMContentLoaded", () => {

    // تهيئة نموذج تعديل بيانات المتجر الموحد
    const form = document.getElementById("store_form");

    if (!form) return;

    const logoInput = document.getElementById("id_logo");
    const logoPreview = document.getElementById("logo_preview");
    const replaceLogoBtn = document.getElementById("replace_logo_btn");

    let originalLogoSrc = logoPreview ? logoPreview.src : "";

    /*
     * تحديث روابط حسابات التواصل
     */
    function updateSocialLinks() {

        // تحديث روابط حسابات التواصل بناءً على القيم الحالية
        const facebook = document.getElementById("id_facebook");
        const instagram = document.getElementById("id_instagram");
        const tiktok = document.getElementById("id_tiktok");
        const telegram = document.getElementById("id_telegram");
        const phone = document.getElementById("id_phone_number1");

        const facebookLink = document.getElementById("facebook_link");
        const instagramLink = document.getElementById("instagram_link");
        const tiktokLink = document.getElementById("tiktok_link");
        const telegramLink = document.getElementById("telegram_link");
        const phoneLink = document.getElementById("phone_link");


        if (facebook && facebookLink) {
            facebookLink.href = facebook.value.trim()
                ? facebook.value.trim()
                : "#";
        }


        if (instagram && instagramLink) {
            instagramLink.href = instagram.value.trim()
                ? instagram.value.trim()
                : "#";
        }


        if (tiktok && tiktokLink) {
            tiktokLink.href = tiktok.value.trim()
                ? tiktok.value.trim()
                : "#";
        }


        if (telegram && telegramLink) {
            telegramLink.href = telegram.value.trim()
                ? telegram.value.trim()
                : "#";
        }


        if (phone && phoneLink) {

            const phoneNumber = phone.value.trim();

            phoneLink.href = phoneNumber
                ? `tel:${phoneNumber}`
                : "#";
        }
    }

    const imageSize = document.getElementById("image-size");
    const imageType = document.getElementById("image-type");
    /*
    * تحديث معلومات الصورة
    */
    function updateImageInfo(file) {

        // تحديث حجم ونوع الصورة
        if (!file) return;

        if (imageSize) {
            imageSize.textContent = `الحجم: ${(file.size / (1024 * 1024)).toFixed(2)} MB`;
        }

        if (imageType) {
            imageType.textContent = `النوع: ${file.type}`;
        }
    }


    /*
     * معاينة الشعار الجديد
     */
    function previewLogo(file) {

        // إعادة المعاينة إلى الشعار الحالي
        if (!file) {

            if (logoPreview) {
                logoPreview.src = originalLogoSrc;
            }

            return;
        }


        // التحقق من أن الملف صورة
        if (!file.type.startsWith("image/")) {

            showToast(
                "failed-toast",
                "يرجى اختيار صورة فقط"
            );

            logoInput.value = "";

            return;
        }


        // التحقق من حجم الصورة
        if (file.size > 10 * 1024 * 1024) {

            showToast(
                "failed-toast",
                "حجم الصورة كبير، الحد الأقصى 10MB"
            );

            logoInput.value = "";

            return;
        }

        updateImageInfo(file);
        const reader = new FileReader();


        reader.onload = function (e) {

            if (logoPreview) {
                logoPreview.src = e.target.result;
            }

        };


        reader.readAsDataURL(file);
    }


    /*
     * فتح نافذة اختيار الشعار
     */
    if (replaceLogoBtn && logoInput) {

        replaceLogoBtn.addEventListener("click", () => {

            // فتح اختيار الصورة
            logoInput.click();
        });
    }


    /*
     * مراقبة اختيار صورة جديدة
     */
    if (logoInput) {

        logoInput.addEventListener("change", () => {

            // تحديث معاينة الشعار
            const file = logoInput.files[0];

            previewLogo(file);
        });
    }

    /*
     * إرسال النموذج بالكامل
     */
    form.addEventListener("submit", async function (event) {
        // إرسال نموذج المتجر وحفظ التعديلات عبر AJAX
        event.preventDefault();
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
                    data.message || "تم حفظ تعديلات المتجر بنجاح"
                );
                setTimeout(() => {
                    window.location.reload();
                }, 500);
                

                
                return;
            }

            if (data.status === "error") {
                // عرض أخطاء الحقول
                Object.entries(data.errors || {}).forEach(([fieldName, errors]) => {

                    const field = document.getElementById(`id_${fieldName}`);

                    if (!field) {
                        return;
                    }
                    const fieldContainer = field.closest(".field");
                    if (fieldContainer) {
                        fieldContainer.classList.add("has-error");
                    }
                });

                return;
            }

        } catch (error) {
            showToast(
                "failed-toast",
                "حدث خطأ ما"
            );
        }
    });

    /*
     * إعادة النموذج إلى بياناته الأصلية
     */
    form.addEventListener("reset", () => {

        // إعادة معاينة الشعار بعد إعادة التعيين
        setTimeout(() => {

            if (logoInput) {
                logoInput.value = "";
            }


            if (logoPreview) {
                logoPreview.src = originalLogoSrc;
            }


            /*
             * تحديث القوائم المخصصة
             */
            const selects = form.querySelectorAll("select");

            selects.forEach(select => {

                select.dispatchEvent(
                    new Event("change", {
                        bubbles: true
                    })
                );
            });


            /*
             * تحديث روابط التواصل
             */
            updateSocialLinks();

        }, 0);
    });

    /*
    * تحميل معلومات الشعار الحالي عند تحميل الصفحة
    */
    if (logoPreview) {

        fetch(logoPreview.src)
            .then(response => response.blob())
            .then(blob => {
                updateImageInfo(blob);
            })
            .catch(() => {});
    }

    /*
     * تحديث الروابط عند تحميل الصفحة
     */
    updateSocialLinks();

});