// =========================================================================
// دالة فتح قائمة المشاركة
function shareProduct() {
    // فتح قائمة المشاركة الأصلية
    if (navigator.share) {
        navigator.share({
            title: document.title,
            url: window.location.href
        });
    }
}
// =========================================================================
// دالة  زر الرجوع للصفحة السابقة
function goBack() {
    // نتحقق هل يوجد صفحة سابقة في history جاء منها المستخدم من نفس الموقع
    if (document.referrer && document.referrer.includes(window.location.hostname)) {
      window.history.back();
    } else {
      // لا يوجد صفحة سابقة من نفس الموقع، نوجه للرئيسية
      window.location.href = "/"; // أو ضع رابط الصفحة الرئيسية الكامل
    }
}
// =========================================================================
// التحكم في الصورة الرئيسية والتنقل بينها
// إنشاء معرض الصور الثانوية أولًا
const productThumbs = new Swiper(".product-thumbs-swiper", {

    slidesPerView: "auto",

    spaceBetween: 10,

    freeMode: true,

    watchSlidesProgress: true,

    direction: "horizontal",

    grabCursor: true,

    breakpoints: {
        768: {
            spaceBetween: 12
        }
    }

});

const productMain = new Swiper(".product-main-swiper", {

    slidesPerView: 1,
    spaceBetween: 0,
    loop: true,
    speed: 350,
    grabCursor: true,
    resistanceRatio: 0,

    pagination: {
        el: ".product-main-swiper .swiper-pagination",
        clickable: true,
        dynamicBullets: true,
        dynamicMainBullets: 5 // عدد النقاط "الكبيرة" الظاهرة في المنتصف
    },

    thumbs: {
        swiper: productThumbs
    }

});
// ===== التكبير عند النقر على الصورة =====
const lightboxEl = document.querySelector(".product-lightbox");
const lightboxWrapper = document.querySelector(".product-lightbox-swiper .swiper-wrapper");
const closeBtn = document.querySelector(".lightbox-close");
// بناء شرائح اللايت بوكس من نفس صور المعرض الرئيسي (مرة واحدة عند التحميل)
document.querySelectorAll(".product-main-swiper .swiper-slide img").forEach((img) => {
    const slide = document.createElement("div");
    slide.className = "swiper-slide";
    slide.innerHTML = `
        <div class="swiper-zoom-container">
            <img src="${img.src}" alt="${img.alt}">
        </div>
    `;
    lightboxWrapper.appendChild(slide);
});
// إنشاء سويبر اللايت بوكس (يُبنى مرة وحدة، بدون loop حتى تشتغل خاصية zoom بشكل صحيح)
const lightboxSwiper = new Swiper(".product-lightbox-swiper", {
    zoom: {
        maxRatio: 4,
        minRatio: 1
    },
    slidesPerView: 1,
    spaceBetween: 0,

    pagination: {
        el: ".product-lightbox-swiper .swiper-pagination",
        clickable: true,
        dynamicBullets: true,
        dynamicMainBullets: 5
    }
});
// فتح اللايت بوكس عند الضغط على أي صورة رئيسية
document.querySelectorAll(".product-main-swiper .swiper-slide").forEach((slide, index) => {
    slide.querySelector("img").addEventListener("click", () => {
        lightboxEl.classList.add("active");
        document.body.style.overflow = "hidden"; // يمنع تمرير الخلفية

        // التزامن مع نفس الشريحة الحالية في المعرض الرئيسي
        lightboxSwiper.slideTo(productMain.realIndex, 0);
    });
});
// إغلاق اللايت بوكس
function closeLightbox() {
    lightboxEl.classList.remove("active");
    document.body.style.overflow = "";

    // إعادة تصغير أي صورة كانت مكبّرة، عشان ما تظل مكبرة لو رجع يفتح
    lightboxSwiper.slides.forEach((slideEl) => {
        if (lightboxSwiper.zoom) {
            lightboxSwiper.zoom.out();
        }
    });
}
closeBtn.addEventListener("click", closeLightbox);
// إغلاق بالضغط خارج الصورة 
lightboxEl.addEventListener("click", (e) => {
    if (e.target === lightboxEl) {
        closeLightbox();
    }
});
// =========================================================================
// إظهار وإخفاء باقي وصف المنتج
// إظهار زر عرض المزيد فقط إذا تجاوز الوصف سطرين 
const description = document.getElementById("productDescription"); 
const button = document.querySelector(".show-more"); 
if (description && button) { 
    if (description.scrollHeight > description.clientHeight) { 
        button.hidden = false; 
    } 
}
function toggleDescription() {

    const description = document.getElementById("productDescription");
    const button = document.querySelector(".show-more");

    description.classList.toggle("collapsed");

    button.textContent = description.classList.contains("collapsed")
        ? "عرض المزيد..."
        : "عرض أقل";
}
// =========================================================================
// إظهار وإخفاء حقل الملاحظات
const showNote = document.getElementById("show_note");
const showNoteField = document.getElementById("show-note-field");
const noteField = document.getElementById("note-field");

showNote.addEventListener("change", function () {
    showNoteField.classList.toggle("hidden", this.checked);
    noteField.classList.toggle("hidden", !this.checked);
});
// =========================================================================
//  عرض المقاسات المرتبطة باللون المحدد فقط وتحديد أول مقاس تلقائيًا
const product = document.getElementById("product-options");
setupProductSizes(product);
// =========================================================================
