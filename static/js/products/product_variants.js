// الكود المسؤول عن التعامل مع خيارات المنتج (الألوان والأحجام)  عرض المقاسات المرتبطة باللون المحدد فقط وتحديد أول مقاس تلقائيًا 
// صفحة بيع المنتج للزبن + صفحة انشاء طلب يدوي من البائع + صفحة تعديل طلب واضافة منتجات اليه
function setupProductSizes(product) {
    // التحقق من وجود عنصر المنتج.
    if (!product) {
        return;
    }
    const colorInputs = product.querySelectorAll(
        "input[name^='color_']"
    );

    const sizeGroups = product.querySelectorAll(
        ".size-group"
    );

    function updateSizes(colorId) {
        // تحديث المقاسات وتحديد أول مقاس من اللون المحدد
        sizeGroups.forEach(group => {
            const isSelected =
                group.dataset.colorId === colorId;

            group.hidden = !isSelected;

            const sizeInputs = group.querySelectorAll(
                "input[type='radio']"
            );

            if (isSelected) {
                const firstSize = sizeInputs[0];

                if (firstSize) {
                    firstSize.checked = true;
                }
            } else {
                sizeInputs.forEach(input => {
                    input.checked = false;
                });
            }
        });
    }

    colorInputs.forEach(input => {
        input.addEventListener("change", function () {
            updateSizes(this.value);
        });
    });

    const selectedColor = product.querySelector(
        "input[name^='color_']:checked"
    );

    if (selectedColor) {
        updateSizes(selectedColor.value);
    }
}