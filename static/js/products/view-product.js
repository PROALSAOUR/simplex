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
// دوال السلة
// (تعمل  مع ملف cart.js)

// عرض السلة المصغرة وملخص الطلب في صفحة بيع المنتج.
function renderCart() {
    // الحصول على عناصر السلة المصغرة وقالبها.
    const cartSection = document.getElementById("cart");
    const cartItems = document.querySelector("#cart .cart-items");
    const cartTemplate = document.getElementById("cart-item-template");

    // الحصول على عناصر ملخص الطلب وقالبها.
    const checkoutItems = document.getElementById("checkout-cart-items");
    const checkoutTemplate = document.getElementById(
        "checkout-cart-item-template"
    );

    // التحقق من وجود العناصر المطلوبة.
    if (
        !cartSection ||
        !cartItems ||
        !cartTemplate ||
        !checkoutItems ||
        !checkoutTemplate
    ) {
        return;
    }

    // إفراغ الحاويتين دون حذف القوالب.
    cartItems.replaceChildren();
    checkoutItems.replaceChildren();

    // إعادة بناء السلة المصغرة وملخص الطلب.
    cartProducts.forEach((item, index) => {
        // إنشاء بطاقة للسلة المصغرة.
        const cartFragment = cartTemplate.content.cloneNode(true);
        const cartItem = cartFragment.querySelector(".cart-item");

        cartItem.querySelector(".item-image").src = item.product_image;
        cartItem.querySelector(".item-image").alt = item.product_name;

        cartItem.querySelector(".item-color").textContent = item.color_name;
        cartItem.querySelector(".item-size").textContent = item.size_name;
        cartItem.querySelector(".item-qty").textContent = item.qty;
        cartItem.querySelector(".item-price").textContent = item.product_price;

        cartItem.querySelector(".item-total").textContent =
            item.product_price * item.qty;

        // حذف العنصر المحدد من السلة.
        cartItem.querySelector(".remove").addEventListener("click", () => {
            removeCartItem(index);
        });

        cartItems.appendChild(cartFragment);

        // إنشاء بطاقة مستقلة لملخص الطلب.
        const checkoutFragment = checkoutTemplate.content.cloneNode(true);
        const checkoutItem = checkoutFragment.querySelector(".cart-item");

        checkoutItem.querySelector(".item-image").src = item.product_image;
        checkoutItem.querySelector(".item-image").alt = item.product_name;

        checkoutItem.querySelector(".item-color").textContent = item.color_name;
        checkoutItem.querySelector(".item-size").textContent = item.size_name;
        checkoutItem.querySelector(".item-qty").textContent = item.qty;

        checkoutItem.querySelector(".item-total").textContent =
            item.product_price * item.qty;

        checkoutItems.appendChild(checkoutFragment);
    });

    // حساب إجمالي سعر السلة.
    const summary = getCartSummary();

    // تحديث الإجمالي في السلة المصغرة وملخص الطلب.
    document.querySelectorAll(".cart-total-price").forEach(element => {
        element.innerHTML =
            `${summary.totalPrice}<span class="currency">د.ل</span>`;
    });

    // إظهار السلة عند وجود عناصر فيها.
    cartSection.hidden = cartProducts.length === 0;
}

// إظهار نموذج تأكيد الطلب وإخفاء صفحة المنتج.
function showCartForm() {
    // منع الانتقال إذا كانت السلة فارغة.
    if (cartProducts.length === 0) return;

    const productPage = document.getElementById("product_page");
    const cartSection = document.getElementById("cart");
    const cartForm = document.getElementById("cart_form");

    if (!productPage || !cartSection || !cartForm) return;

    // تحديث ملخص الطلب قبل إظهار النموذج.
    renderCart();

    // إخفاء صفحة المنتج والسلة المصغرة.
    productPage.hidden = true;
    cartSection.hidden = true;

    // إظهار نموذج الشراء.
    cartForm.hidden = false;

    // العودة إلى أعلى الصفحة.
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

//  العودة إلى صفحة المنتج والسلة المصغرة.
function hideCartForm() {
    // الحصول على عناصر الصفحة.
    const productPage = document.getElementById("product_page");
    const cartSection = document.getElementById("cart");
    const cartForm = document.getElementById("cart_form");

    if (!productPage || !cartSection || !cartForm) return;

    // إخفاء النموذج وإظهار صفحة المنتج.
    cartForm.hidden = true;
    productPage.hidden = false;

    // إظهار السلة المصغرة إذا كانت تحتوي على عناصر.
    cartSection.hidden = cartProducts.length === 0;

    // تحديث السلة بعد العودة.
    renderCart();
}

// ربط أزرار التنقل بعد تحميل الصفحة.
document.addEventListener("DOMContentLoaded", () => {
    // زر إتمام الطلب.
    const checkoutButton = document.getElementById("checkout-button");

    if (checkoutButton) {
        checkoutButton.addEventListener("click", showCartForm);
    }

    // زر العودة إلى المنتج.
    const backButton = document.querySelector("#cart_form .hide-form");

    if (backButton) {
        backButton.type = "button";

        backButton.addEventListener("click", event => {
            event.preventDefault();
            hideCartForm();
        });
    }
});

// إرسال الطلب عند تقديم النموذج.
document.getElementById("cart_form")?.addEventListener("submit", event => {
    event.preventDefault();
    submitOrder(event.currentTarget);
});
// =========================================================================
