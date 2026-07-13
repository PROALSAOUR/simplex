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

        // هذا الجزء من الكود يقوم بتهيئة بطاقات المنتجات بعد عرضها في نافذة البحث وهذه الدالة مكتوبة داخل ملف product_cart.js
        resultsContainer.querySelectorAll(".product-container").forEach(container => { initializeProductCard(container); });

    } catch(error){

        console.error(error);

    }
}
});