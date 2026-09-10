function setupCustomerEdit() {

    const customerList = document.getElementById("customer-list");
    const customerForm = document.getElementById("customer-form");

    // تحقق من وجود العناصر المطلوبة
    if (!customerList || !customerForm) {
        return;
    }

    const editButton = customerList.querySelector(".edit-btn");
    const cancelButton = customerForm.querySelector(".edit-btn");

    // تحقق من وجود الأزرار المطلوبة
    if (!editButton || !cancelButton) {
        return;
    }


    // ---------------------------------------------
    // الحالة الافتراضية
    // ---------------------------------------------

    customerList.hidden = false;
    customerForm.hidden = true;


    // ---------------------------------------------
    // إذا كان هناك خطأ في الفورم
    // أبقِ قائمة التعديل مفتوحة
    // ---------------------------------------------

    if (customerForm.classList.contains("has-errors")) {
        customerList.hidden = true;
        customerForm.hidden = false;
    }


    // ---------------------------------------------
    // فتح قائمة التعديل
    // ---------------------------------------------

    editButton.addEventListener("click", function () {

        customerList.hidden = true;
        customerForm.hidden = false;

    });


    // ---------------------------------------------
    // إلغاء التعديل
    // ---------------------------------------------

    cancelButton.addEventListener("click", function () {

        customerForm.hidden = true;
        customerList.hidden = false;

    });
}


setupCustomerEdit();