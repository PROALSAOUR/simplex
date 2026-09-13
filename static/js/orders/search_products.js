// يتم استخدام هذا الملف في مكانين الاول صفحة انشاء طلب يدويا والثاني صفحة تعديل طلب تحديدا اضافة منتج الى طلب
// الكود المسؤول عن البحث عن المنتجات في قاعدة البيانات وعرضها للمستخدم
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("product-search");
    const searchUrl = searchInput.dataset.searchUrl;
    const resultsContainer = document.getElementById("search-results");
    const buttonType = resultsContainer.dataset.productButtonType;
    let searchTimer;
    searchInput.addEventListener("input", function(){
        const query = this.value.trim();
        clearTimeout(searchTimer);
        // إذا كان فارغاً أخفِ النتائج
        if(query.length < 2){
            resultsContainer.innerHTML = "";
            return;
        }
        // انتظار 300ms بعد توقف الكتابة
        searchTimer = setTimeout(() => {
            searchProducts(query);
        }, 300);

    });

    async function searchProducts(query){

    try {

        const response = await fetch(
            `${searchUrl}?q=${encodeURIComponent(query)}&button_type=${buttonType}`
        );


        const html = await response.text();

        resultsContainer.innerHTML = html;

        // دالة تعرض مقاسات اللون المحدد فقط وتخفي الباقي
        resultsContainer.querySelectorAll(".product-card").forEach(card => {
            setupProductSizes(card);
        });
        

    } catch(error){
        console.error(error);
    }
}
});
// ==================================================================================
//  عرض المقاسات المرتبطة باللون المحدد فقط وتحديد أول مقاس تلقائيًا
function setupProductSizes(card) {
    const colorInputs = card.querySelectorAll(
        "input[name^='color_']"
    );

    const sizeGroups = card.querySelectorAll(
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

    const selectedColor = card.querySelector(
        "input[name^='color_']:checked"
    );

    if (selectedColor) {
        updateSizes(selectedColor.value);
    }
}
// ==================================================================================
