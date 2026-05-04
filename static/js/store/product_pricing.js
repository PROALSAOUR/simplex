document.addEventListener("DOMContentLoaded", function () {
    let form = null;
    const offerCheckbox = document.getElementById("id_offer");
    const offerCheckboxField = document.getElementById("offer_checkbox_field");
    const priceInput = document.getElementById("id_price");
    const offerPriceInput = document.getElementById("id_offer_price");
    const priceField = document.getElementById("price_field");
    const offerPriceField = document.getElementById("offer_price_field");
    const offerPercentage = document.getElementById("offer_percentage");
    const purchasePriceInput = document.getElementById("id_purchase_price");

    function getFormFromTarget(target) {
        if (!target) {
            return null;
        }
        if (typeof target === "string") {
            return document.getElementById(target) || document.querySelector(target);
        }
        return target instanceof HTMLFormElement ? target : null;
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
            form.removeEventListener("submit", handleFormSubmit);
        }
        form = formElement;
        initOfferControls();
        bindPricingValidation();
    }

    function getNumericValue(input) {
        const value = input?.value?.trim();
        if (!value) {
            return null;
        }
        const number = parseFloat(value);
        return Number.isFinite(number) ? number : null;
    }

    function setPurchasePriceValidity(message) {
        if (!purchasePriceInput) {
            return;
        }
        purchasePriceInput.setCustomValidity(message || "");
        if (message) {
            purchasePriceInput.reportValidity();
        }
    }

    function validatePurchasePrice() {
        if (!purchasePriceInput || !priceInput) {
            return true;
        }

        const purchasePrice = getNumericValue(purchasePriceInput);
        const regularPrice = getNumericValue(priceInput);
        const offerPrice = getNumericValue(offerPriceInput);
        const hasOffer = offerCheckbox?.checked;

        if (purchasePrice === null) {
            setPurchasePriceValidity("");
            return true;
        }

        if (hasOffer) {
            if (offerPrice === null) {
                setPurchasePriceValidity("");
                return true;
            }
            if (!(purchasePrice < offerPrice)) {
                setPurchasePriceValidity('يجب أن يكون سعر الشراء أقل من سعر التخفيض.');
                return false;
            }
            setPurchasePriceValidity("");
            return true;
        }

        if (regularPrice === null) {
            setPurchasePriceValidity("");
            return true;
        }
        if (!(purchasePrice < regularPrice)) {
            setPurchasePriceValidity('يجب أن يكون سعر الشراء أقل من سعر البيع.');
            return false;
        }

        setPurchasePriceValidity("");
        return true;
    }

    function initOfferControls() {
        if (!offerCheckbox || !offerCheckboxField || !priceInput || !offerPriceInput || !priceField || !offerPriceField || !offerPercentage) {
            return;
        }

        const priceLabel = priceField.querySelector("label");
        const originalNextSibling = priceField.nextElementSibling;

        function setOfferState(isEnabled) {
            if (isEnabled) {
                priceLabel.textContent = "السعر قبل التخفيض";
                offerPriceField.style.display = "block";
                offerPriceInput.required = true;
                offerCheckboxField.after(priceField);
                priceField.after(offerPriceField);
                calculateDiscount();
                return;
            }

            priceLabel.textContent = "سعر البيع";
            offerPriceField.style.display = "none";
            offerPercentage.style.display = "none";
            offerPriceInput.value = "";
            offerPriceInput.required = false;

            if (originalNextSibling) {
                originalNextSibling.before(priceField);
            }
        }

        function calculateDiscount() {
            const originalPrice = parseFloat(priceInput.value);
            const discountedPrice = parseFloat(offerPriceInput.value);

            if (isNaN(originalPrice) || isNaN(discountedPrice)) {
                offerPercentage.style.display = "none";
                offerPriceInput.setCustomValidity("");
                return;
            }

            if (discountedPrice >= originalPrice) {
                offerPriceInput.setCustomValidity("يجب أن يكون السعر بعد التخفيض أقل من السعر قبل التخفيض");
                offerPriceInput.reportValidity();
                offerPercentage.style.display = "none";
                return;
            }

            offerPriceInput.setCustomValidity("");
            const percentage = ((originalPrice - discountedPrice) / originalPrice) * 100;
            offerPercentage.style.display = "inline-block";
            offerPercentage.textContent = "نسبة التخفيض " + percentage.toFixed(1) + "%";
        }

        offerCheckbox.addEventListener("change", function () {
            setOfferState(this.checked);
        });

        priceInput.addEventListener("input", calculateDiscount);
        offerPriceInput.addEventListener("input", calculateDiscount);
        purchasePriceInput?.addEventListener("input", () => setPurchasePriceValidity(""));

        setOfferState(offerCheckbox.checked);
    }

    function handleFormSubmit(event) {
        if (!validatePurchasePrice()) {
            event.preventDefault();
        }
    }

    function bindPricingValidation() {
        if (!form) {
            return;
        }

        form.addEventListener("submit", handleFormSubmit);
    }

    setForm("add_product_form");

    window.SimplexPricingManager = {
        setForm,
        validatePurchasePrice,
    };
});
