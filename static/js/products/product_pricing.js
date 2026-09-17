document.addEventListener("DOMContentLoaded", function () {
    // تهيئة مدير التسعير والتحقق من حقول الأسعار

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
            form.removeEventListener("submit", handleFormSubmit);
        }

        form = formElement;

        initOfferControls();
        bindPricingValidation();
    }


    function getNumericValue(input) {
        // تحويل قيمة حقل السعر إلى رقم صالح أو إرجاع null
        const value = input?.value?.trim();

        if (!value) {
            return null;
        }

        const number = parseFloat(value);

        return Number.isFinite(number)
            ? number
            : null;
    }


    function sanitizeDecimalInput(input) {
        // السماح بالأرقام وعلامة عشرية واحدة فقط داخل حقل السعر
        if (!input) {
            return;
        }

        let value = input.value.replace(/[^\d.]/g, "");

        const decimalIndex = value.indexOf(".");

        if (decimalIndex !== -1) {
            value =
                value.substring(0, decimalIndex + 1) +
                value.substring(decimalIndex + 1).replace(/\./g, "");
        }

        input.value = value;
    }


    function formatNumber(value) {
        // تنسيق الرقم وإزالة الأصفار غير الضرورية بعد العلامة العشرية
        if (!Number.isFinite(value)) {
            return "";
        }

        return Number(value.toFixed(2)).toString();
    }


    function updateValueStatus(element, value) {
        // تطبيق حالة الربح أو الخسارة على العنصر
        if (!element) {
            return;
        }

        element.classList.remove("complete", "cancel");

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

        offerPriceInput.setCustomValidity(message || "");
    }


    function validateOfferPrice() {
        // التحقق من أن سعر التخفيض أقل من السعر الأصلي
        if (
            !offerCheckbox?.checked ||
            !offerPriceInput ||
            !priceInput
        ) {
            setOfferPriceValidity("");
            return true;
        }

        const regularPrice = getNumericValue(priceInput);
        const offerPrice = getNumericValue(offerPriceInput);

        if (
            regularPrice === null ||
            offerPrice === null
        ) {
            setOfferPriceValidity("");
            return true;
        }

        if (offerPrice >= regularPrice) {
            setOfferPriceValidity(
                "يجب أن يكون سعر التخفيض أقل من السعر قبل التخفيض."
            );

            return false;
        }

        setOfferPriceValidity("");

        return true;
    }


    function updateProfitLabels(profit) {
        // تحديث تسميات الربح أو الخسارة حسب النتيجة الحالية
        const profitLabel =
            profitValue
                ?.closest(".s-item")
                ?.querySelector(".s-title");

        const profitMarginLabel =
            profitMarginValue
                ?.closest(".s-item")
                ?.querySelector(".s-title");


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


    function resetPricingSummary() {
        // إخفاء ملخص التسعير ومسح قيمه عند عدم اكتمال الأسعار
        if (!pricingSummary) {
            return;
        }

        pricingSummary.style.display = "none";

        if (profitValue) {
            profitValue.textContent = "";
            updateValueStatus(profitValue, 0);
        }

        if (profitMarginValue) {
            profitMarginValue.textContent = "";
            updateValueStatus(profitMarginValue, 0);
        }
    }


    function updatePricingSummary() {
        // حساب الربح والخسارة والخصم وتحديث ملخص التسعير
        if (
            !pricingSummary ||
            !purchasePriceInput ||
            !priceInput ||
            !profitValue ||
            !profitMarginValue
        ) {
            return;
        }

        const purchasePrice = getNumericValue(purchasePriceInput);
        const regularPrice = getNumericValue(priceInput);

        const hasOffer = offerCheckbox?.checked;

        const discountedPrice = getNumericValue(offerPriceInput);


        if (
            purchasePrice === null ||
            regularPrice === null
        ) {
            resetPricingSummary();
            return;
        }


        let actualSellingPrice = regularPrice;

        if (
            hasOffer &&
            discountedPrice !== null
        ) {
            actualSellingPrice = discountedPrice;
        }


        pricingSummary.style.display = "";


        const profit =
            actualSellingPrice - purchasePrice;


        updateProfitLabels(profit);


        profitValue.textContent =
            formatNumber(Math.abs(profit));


        updateValueStatus(
            profitValue,
            profit
        );


        if (purchasePrice !== 0) {

            const profitMargin =
                (profit / purchasePrice) * 100;

            profitMarginValue.textContent =
                formatNumber(Math.abs(profitMargin)) + "%";

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


        if (
            hasOffer &&
            discountedPrice !== null &&
            discountedPrice < regularPrice
        ) {

            const discountValue =
                regularPrice - discountedPrice;

            const discountPercentage =
                (discountValue / regularPrice) * 100;


            if (offerValueItem) {
                offerValueItem.style.display = "flex";
            }

            if (offerValue) {
                offerValue.textContent =
                    formatNumber(discountValue);
            }


            if (offerPercentageItem) {
                offerPercentageItem.style.display = "flex";
            }

            if (offerPercentage) {
                offerPercentage.textContent =
                    "-" +
                    formatNumber(discountPercentage) +
                    "%";
            }

        } else {

            if (offerValueItem) {
                offerValueItem.style.display = "none";
            }

            if (offerPercentageItem) {
                offerPercentageItem.style.display = "none";
            }

            if (offerValue) {
                offerValue.textContent = "";
            }

            if (offerPercentage) {
                offerPercentage.textContent = "";
            }
        }
    }


    function setOfferState(isEnabled) {
        // إظهار أو إخفاء حقل التخفيض وتحديث تسمية سعر البيع
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
                Array.from(priceLabel.childNodes).forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        node.textContent =
                            "السعر قبل التخفيض ";
                    }
                });
            }

            if (requiredStar) {
                requiredStar.style.display = "";
            }

            offerPriceField.style.display = "block";
            offerPriceInput.required = true;

        } else {

            if (priceLabel) {
                Array.from(priceLabel.childNodes).forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        node.textContent =
                            "سعر البيع ";
                    }
                });
            }

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


    function handlePriceInput(input) {
        // تنظيف حقل السعر ثم تحديث التحقق والحسابات
        sanitizeDecimalInput(input);

        setOfferPriceValidity("");

        updatePricingSummary();

        validateOfferPrice();
    }


    function initOfferControls() {
        // تهيئة التحكم بالتخفيض وحقول الأسعار
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

        offerCheckbox.addEventListener(
            "change",
            function () {
                setOfferState(this.checked);
            }
        );

        [
            purchasePriceInput,
            priceInput,
            offerPriceInput
        ].forEach(input => {

            input?.addEventListener(
                "input",
                function () {
                    handlePriceInput(this);
                }
            );

        });

        if (form) {
            form.addEventListener(
                "reset",
                function () {
                    // انتظار انتهاء إعادة تعيين النموذج ثم تحديث حالة التخفيض
                    setTimeout(function () {
                        setOfferState(offerCheckbox.checked);
                    }, 0);
                }
            );
        }

        setOfferState(
            offerCheckbox.checked
        );
    }

    function handleFormSubmit(event) {
        // منع إرسال النموذج عند وجود سعر تخفيض غير صحيح
        if (!validateOfferPrice()) {
            event.preventDefault();

            offerPriceInput?.reportValidity();
        }
    }


    function bindPricingValidation() {
        // ربط التحقق من سعر التخفيض بإرسال النموذج
        if (!form) {
            return;
        }

        form.addEventListener(
            "submit",
            handleFormSubmit
        );
    }


    setForm("product_form");


    window.SimplexPricingManager = {
        setForm,
        validateOfferPrice,
        updatePricingSummary
    };

});