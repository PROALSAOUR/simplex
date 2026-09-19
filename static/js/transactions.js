// هذه الدالة تعمل بصفحة عرض الطلب وعرض الفاتورة للتبديل بين قوائم العرض والتعديل
function setupDetailsEdit() {
    // إعداد التبديل بين قوائم العرض والتعديل داخل كل details

    const detailsElements = document.querySelectorAll(".details");

    if (!detailsElements.length) {
        return;
    }

    detailsElements.forEach(function (details) {

        const lists = details.querySelectorAll(".details-list");

        // نحتاج إلى قائمتين على الأقل
        if (lists.length < 2) {
            return;
        }

        // إخفاء جميع القوائم ما عدا الأولى
        lists.forEach(function (list, index) {
            list.hidden = index !== 0;
        });


        // جميع أزرار التعديل/الإلغاء داخل هذا details
        const editButtons = details.querySelectorAll(".edit-btn");

        editButtons.forEach(function (button) {

            button.addEventListener("click", function () {

                // معرفة القائمة التي يوجد بداخلها الزر الذي تم الضغط عليه
                const currentList = button.closest(".details-list");

                if (!currentList) {
                    return;
                }

                // البحث عن القائمة الأخرى داخل نفس details
                const targetList = Array.from(lists).find(function (list) {
                    return list !== currentList;
                });

                if (!targetList) {
                    return;
                }

                // إخفاء القائمة الحالية وإظهار القائمة الأخرى
                currentList.hidden = true;
                targetList.hidden = false;

            });

        });

    });
}

setupDetailsEdit();
// ===============================================================================