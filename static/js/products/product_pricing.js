document.addEventListener("DOMContentLoaded", function () {

    let form = null;

    const offerCheckbox = document.getElementById("offer");
    const offerCheckboxField = document.getElementById("offer_checkbox_field");

    const purchasePriceInput = document.getElementById("purchase_price");
    const priceInput = document.getElementById("price");
    const offerPriceInput = document.getElementById("offer_price");

    const priceField = document.getElementById("price_field");
    const offerPriceField = document.getElementById("offer_price_field");

    const pricingSummary = document.getElementById("pricing-summary");

    const profitValue = document.getElementById("profit_value");
    const profitMarginValue = document.getElementById("profit_margin_value");

    const offerValueItem = document.getElementById("offer_value_item");
    const offerValue = document.getElementById("offer_value");

    const offerPercentageItem = document.getElementById(
        "offer_percentage_item"
    );

    const offerPercentage = document.getElementById(
        "offer_percentage"
    );

    function getFormFromTarget(target) {
        // الحصول على النموذج سواء تم تمرير عنصر النموذج أو معرفه أو محدد CSS
        if (!target) {
            return null;
        }

        if (typeof target === "string") {
            return (
                document.getElementById(target) ||
                document.querySelector(target)
            );
        }

        return target instanceof HTMLFormElement
            ? target
            : null;
    }

    function setForm(target) {
        // ربط مدير التسعير بالنموذج المحدد وإعادة تهيئة التحقق والحسابات
        const formElement = getFormFromTarget(target);

        if (!formElement || form === formElement) {
            return;
        }

        if (form) {
            form.removeEventListener(
                "submit",
                handleFormSubmit
            );
        }

        form = formElement;

        initOfferControls();
        bindPricingValidation();
    }

    function getNumericValue(input) {
        // تحويل قيمة حقل السعر إلى رقم صالح أو إرجاع null إذا كانت القيمة غير صالحة
        const value = input?.value?.trim();

        if (!value) {
            return null;
        }

        const number = parseFloat(value);

        return Number.isFinite(number)
            ? number
            : null;
    }

    function formatNumber(value) {
        // تنسيق الرقم وإزالة الأصفار غير الضرورية بعد العلامة العشرية
        if (!Number.isFinite(value)) {
            return "";
        }

        return Number(
            value.toFixed(2)
        ).toString();
    }

    function updateValueStatus(element, value) {
        // تطبيق كلاس الربح أو الخسارة حسب قيمة الرقم مع إزالة الكلاسات القديمة
        if (!element) {
            return;
        }

        element.classList.remove(
            "complete",
            "cancel"
        );

        if (value > 0) {
            element.classList.add("complete");
        } else if (value < 0) {
            element.classList.add("cancel");
        }
    }

    function setOfferPriceValidity(message) {
        // ضبط أو إزالة رسالة التحقق الخاصة بسعر التخفيض
        if (!offerPriceInput) {
            return;
        }

        offerPriceInput.setCustomValidity(
            message || ""
        );
    }

    function validateOfferPrice() {
        // التحقق من أن سعر التخفيض أقل من السعر الأصلي دون منع البيع بخسارة
        if (
            !offerCheckbox?.checked ||
            !offerPriceInput ||
            !priceInput
        ) {
            setOfferPriceValidity("");
            return true;
        }

        const regularPrice = getNumericValue(
            priceInput
        );

        const offerPrice = getNumericValue(
            offerPriceInput
        );

        if (
            regularPrice === null ||
            offerPrice === null
        ) {
            setOfferPriceValidity("");
            return true;
        }

        /*
         * سعر التخفيض يجب أن يكون أقل
         * من السعر قبل التخفيض.
         */
        if (offerPrice >= regularPrice) {
            setOfferPriceValidity(
                "يجب أن يكون سعر التخفيض أقل من السعر قبل التخفيض."
            );

            return false;
        }

        /*
         * لا نتحقق من سعر التكلفة هنا.
         *
         * البيع بخسارة مسموح، وسيتم توضيحه
         * في ملخص التسعير من خلال كلاس cancel.
         */
        setOfferPriceValidity("");

        return true;
    }

    function updateProfitLabels(profit, profitMargin) {
        // تغيير مسميات الربح إلى الخسارة حسب نتيجة التسعير
        const profitLabel =
            profitValue?.closest(".s-item")?.querySelector(".s-title");

        const profitMarginLabel =
            profitMarginValue?.closest(".s-item")?.querySelector(".s-title");


        if (profit > 0) {

            if (profitLabel) {
                profitLabel.textContent = "قيمة الربح";
            }

            if (profitMarginLabel) {
                profitMarginLabel.textContent = "نسبة الربح";
            }

        } else if (profit < 0) {

            if (profitLabel) {
                profitLabel.textContent = "قيمة الخسارة";
            }

            if (profitMarginLabel) {
                profitMarginLabel.textContent = "نسبة الخسارة";
            }

        } else {

            if (profitLabel) {
                profitLabel.textContent = "قيمة الربح";
            }

            if (profitMarginLabel) {
                profitMarginLabel.textContent = "نسبة الربح";
            }
        }
    }

    function updatePricingSummary() {
        // حساب الربح أو الخسارة ونسبته وقيمة الخصم ونسبته وتحديث حالتها البصرية
        if (
            !pricingSummary ||
            !purchasePriceInput ||
            !priceInput ||
            !profitValue ||
            !profitMarginValue
        ) {
            return;
        }

        const purchasePrice = getNumericValue(
            purchasePriceInput
        );

        const regularPrice = getNumericValue(
            priceInput
        );

        const hasOffer = offerCheckbox?.checked;

        const discountedPrice = getNumericValue(
            offerPriceInput
        );


        /*
         * لا نعرض الملخص إلا بعد إدخال
         * سعر التكلفة وسعر البيع الأساسي.
         */
        if (
            purchasePrice === null ||
            regularPrice === null
        ) {
            pricingSummary.style.display = "none";

            profitValue.textContent = "";
            profitMarginValue.textContent = "";

            updateValueStatus(
                profitValue,
                0
            );

            updateValueStatus(
                profitMarginValue,
                0
            );

            return;
        }


        /*
         * تحديد السعر الفعلي الذي سيدفعه الزبون.
         *
         * مع التخفيض:
         * السعر الفعلي = سعر التخفيض.
         *
         * بدون تخفيض:
         * السعر الفعلي = سعر البيع.
         */
        let actualSellingPrice = regularPrice;

        if (
            hasOffer &&
            discountedPrice !== null
        ) {
            actualSellingPrice = discountedPrice;
        }


        /*
         * إظهار الملخص بعد توفر الأسعار الأساسية.
         */
        pricingSummary.style.display = "";


        /*
         * حساب قيمة الربح:
         *
         * الربح =
         * سعر البيع الفعلي - سعر التكلفة.
         */
        const profit =
            actualSellingPrice - purchasePrice;


        /*
         * تحديد ما إذا كانت النتيجة
         * ربحًا أو خسارة.
         */
        updateProfitLabels(
            profit,
            null
        );


        /*
         * عند الخسارة نعرض القيمة موجبة،
         * لأن كلمة "الخسارة" توضح اتجاه القيمة.
         */
        profitValue.textContent =
            formatNumber(
                Math.abs(profit)
            );


        /*
         * تطبيق:
         *
         * complete للربح.
         * cancel للخسارة.
         * لا شيء عند التعادل.
         */
        updateValueStatus(
            profitValue,
            profit
        );


        /*
         * حساب نسبة الربح أو الخسارة:
         *
         * النسبة =
         * الربح ÷ سعر التكلفة × 100.
         *
         * استخدام سعر التكلفة كمرجع يجعل
         * النسبة أكثر وضوحًا عند وجود خسارة.
         */
        if (purchasePrice !== 0) {

            const profitMargin =
                (profit / purchasePrice) * 100;


            /*
             * عرض النسبة بدون إشارة سالبة
             * عند وجود خسارة.
             */
            profitMarginValue.textContent =
                formatNumber(
                    Math.abs(profitMargin)
                ) + "%";


            /*
             * تطبيق حالة الربح أو الخسارة
             * على النسبة.
             */
            updateValueStatus(
                profitMarginValue,
                profitMargin
            );

        } else {

            profitMarginValue.textContent = "";

            updateValueStatus(
                profitMarginValue,
                0
            );
        }


        /*
         * حساب قيمة الخصم ونسبته
         * عند وجود تخفيض صالح.
         */
        if (
            hasOffer &&
            discountedPrice !== null &&
            discountedPrice < regularPrice
        ) {

            /*
             * قيمة الخصم =
             *
             * السعر قبل التخفيض -
             * السعر بعد التخفيض.
             */
            const discountValue =
                regularPrice - discountedPrice;


            /*
             * نسبة الخصم =
             *
             * قيمة الخصم ÷
             * السعر قبل التخفيض × 100.
             */
            const discountPercentage =
                (discountValue / regularPrice) * 100;


            offerValueItem.style.display = "flex";

            offerValue.textContent =
                formatNumber(discountValue);


            offerPercentageItem.style.display = "flex";

            offerPercentage.textContent =
                "-" + formatNumber(discountPercentage) + "%";

        } else {

            offerValueItem.style.display = "none";
            offerPercentageItem.style.display = "none";

            offerValue.textContent = "";
            offerPercentage.textContent = "";
        }
    }

    function setOfferState(isEnabled) {
        // إظهار أو إخفاء حقل التخفيض وتحديث تسمية السعر مع إبقاء النجمة
        if (
            !priceField ||
            !offerPriceField ||
            !offerPriceInput
        ) {
            return;
        }

        const priceLabel =
            priceField.querySelector("label");

        const requiredStar =
            priceLabel?.querySelector("span.required");


        if (isEnabled) {

            if (priceLabel) {
                /*
                * تغيير نص الـ label فقط دون المساس
                * بعنصر النجمة الموجود بداخله.
                */
                Array.from(priceLabel.childNodes).forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        node.textContent = "السعر قبل التخفيض ";
                    }
                });
            }

            /*
            * إبقاء نجمة الحقل مطلوبة ظاهرة.
            */
            if (requiredStar) {
                requiredStar.style.display = "";
            }

            offerPriceField.style.display = "block";

            offerPriceInput.required = true;

        } else {

            if (priceLabel) {
                /*
                * إعادة تسمية الحقل دون إزالة النجمة.
                */
                Array.from(priceLabel.childNodes).forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        node.textContent = "سعر البيع ";
                    }
                });
            }

            /*
            * إبقاء نجمة الحقل مطلوبة ظاهرة.
            */
            if (requiredStar) {
                requiredStar.style.display = "";
            }

            offerPriceField.style.display = "none";

            offerPriceInput.required = false;

            offerPriceInput.value = "";

            setOfferPriceValidity("");
        }


        updatePricingSummary();
    }

    function initOfferControls() {
        // تهيئة التحكم في التخفيض وربط حقول الأسعار بالتحديث الفوري
        if (
            !offerCheckbox ||
            !offerCheckboxField ||
            !purchasePriceInput ||
            !priceInput ||
            !offerPriceInput ||
            !priceField ||
            !offerPriceField
        ) {
            return;
        }


        /*
         * تغيير حالة التخفيض عند الضغط
         * على checkbox.
         */
        offerCheckbox.addEventListener(
            "change",
            function () {
                setOfferState(
                    this.checked
                );
            }
        );


        /*
         * تحديث الحسابات أثناء الكتابة
         * في حقول الأسعار.
         */
        [
            purchasePriceInput,
            priceInput,
            offerPriceInput
        ].forEach(input => {

            input?.addEventListener(
                "input",
                function () {

                    /*
                     * إزالة رسائل التحقق القديمة
                     * أثناء تعديل القيمة.
                     */
                    setOfferPriceValidity("");


                    /*
                     * تحديث ملخص التسعير مباشرة.
                     */
                    updatePricingSummary();


                    /*
                     * التحقق من سعر التخفيض فقط
                     * إذا كان التخفيض مفعلاً.
                     */
                    validateOfferPrice();
                }
            );
        });


        /*
         * تطبيق حالة التخفيض الحالية
         * عند تحميل الصفحة.
         */
        setOfferState(
            offerCheckbox.checked
        );


        /*
         * تحديث الملخص عند تحميل الصفحة،
         * وهو مهم خصوصًا في صفحة تعديل المنتج.
         */
        updatePricingSummary();
    }

    function handleFormSubmit(event) {
        // منع إرسال النموذج فقط عند وجود سعر تخفيض غير صحيح
        const offerPriceValid =
            validateOfferPrice();

        if (!offerPriceValid) {

            event.preventDefault();

            offerPriceInput?.reportValidity();
        }
    }

    function bindPricingValidation() {
        // ربط التحقق من الأسعار بحدث إرسال النموذج
        if (!form) {
            return;
        }

        form.addEventListener(
            "submit",
            handleFormSubmit
        );
    }

    /*
     * في صفحة تعديل المنتج يمكن استخدام:
     * SimplexPricingManager.setForm("edit_product_form");
     */
    setForm("add_product_form");

    /*
     * إتاحة مدير التسعير للصفحات الأخرى
     * التي تستخدم نفس نظام التسعير.
     */
    window.SimplexPricingManager = {
        setForm,
        validateOfferPrice,
        updatePricingSummary
    };

});