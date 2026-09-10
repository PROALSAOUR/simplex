// =================================================
// دالة عرض التوست (الرسالة المنبثقة)
function showToast(id, message) {
    const toast = document.getElementById(id);
    toast.innerText = message;
    toast.style.visibility = "visible";
    setTimeout(() => {
        toast.style.visibility = "hidden";
    }, 3000); // يختفي بعد 3 ثواني
}
// =================================================
// دوال  لإدارة القوائم المنسدلة في الهيدر
function setupMenu({
    button,
    wrapper,
    menu,
    closeButton = null,
    overlay = null,
    menuClass = "open",
    buttonClass = "active"
}) {

    // فتح القائمة
    function openMenu() {
        menu.classList.add(menuClass);

        button.classList.add(buttonClass);

        button.setAttribute(
            "aria-expanded",
            "true"
        );
        if(overlay){
            overlay.classList.add("open");
        }
    }

    // إغلاق القائمة
    function closeMenu() {
        menu.classList.remove(menuClass);

        button.classList.remove(buttonClass);

        button.setAttribute(
            "aria-expanded",
            "false"
        );
        if(overlay){
            overlay.classList.remove("open");
        }
    }

    // تبديل حالة القائمة
    function toggleMenu() {

        const isOpen = menu.classList.contains(
            menuClass
        );

        if (isOpen) {
            closeMenu();
        } else {
            openMenu();
        }

    }

    // الضغط على زر الفتح
    if (button) {
        button.addEventListener(
            "click",
            toggleMenu
        );
    }

    // الضغط على زر الإغلاق (إن وجد)
    if (closeButton) {
        closeButton.addEventListener(
            "click",
            closeMenu
        );
    }

    if(overlay){

        overlay.addEventListener(
            "click",
            closeMenu
        );

    }

    // الضغط خارج القائمة
    document.addEventListener(
        "click",
        (event) => {
            if (! wrapper) { return }
            if (!wrapper.contains(event.target)) {
                closeMenu();
            }
        }
    );

}
// ==========================================================
// دالة ازرار الرجوع 
function goBack() {
    // نتحقق هل يوجد صفحة سابقة في history جاء منها المستخدم من نفس الموقع
    if (document.referrer && document.referrer.includes(window.location.hostname)) {
      window.history.back();
    } else {
      // لا يوجد صفحة سابقة من نفس الموقع، نوجه للرئيسية
      window.location.href = "/"; // أو ضع رابط الصفحة الرئيسية الكامل
    }
  }
// ==========================================================
document.addEventListener("DOMContentLoaded",() => {

    // ===== كود فتح واغلاق القوائم المنسدلة في الهيدر =====
        /* قائمة الحساب */
        setupMenu({
            button: document.querySelector(
                ".account-button"
            ),
            wrapper: document.querySelector(
                ".account-wrapper"
            ),
            menu: document.querySelector(
                ".account-menu"
            )
        });
        /*  القائمة الجانبية */
        setupMenu({
            button: document.querySelector(
                ".sidemenu-button"
            ),

            wrapper: document.querySelector(
                ".sidemenu-wrapper"
            ),
            menu: document.querySelector(
                ".side-menu"
            ),
            closeButton: document.querySelector(
                ".side-menu .close-button"
            ),
            overlay: document.querySelector(
                ".menu-overlay"
            )
        });

    // =================================================
    // ===== كود تبديل الوضع الليلي والنهاري =====
        const themeButton = document.querySelector(".theme-toggle");
        const html = document.documentElement;
        // تحميل الثيم المحفوظ
        const savedTheme = localStorage.getItem("theme");
        if (!themeButton) { return }

        if (savedTheme === "dark") {

            html.classList.add("dark-mode");


            themeButton.setAttribute(
                "aria-pressed",
                "true"
            );

            themeButton.setAttribute(
                "aria-label",
                "تفعيل الوضع الفاتح"
            );

        } else {

            themeButton.setAttribute(
                "aria-pressed",
                "false"
            );

            themeButton.setAttribute(
                "aria-label",
                "تفعيل الوضع الغامق"
            );
        }

        themeButton.addEventListener(
            "click",
            (event) => {
                event.preventDefault();

                const isDarkMode =
                    html.classList.toggle("dark-mode");

                themeButton.setAttribute(
                    "aria-pressed",
                    String(isDarkMode)
                );

                themeButton.setAttribute(
                    "aria-label",
                    isDarkMode
                        ? "تفعيل الوضع الفاتح"
                        : "تفعيل الوضع الغامق"
                );

                // حفظ الثيم الصحيح
                localStorage.setItem(
                    "theme",
                    isDarkMode
                        ? "dark"
                        : "light"
                );

            }
        );
    // ==================================================

});
// ==========================================================
// دالة تقوم بتفعيل الرابط الفعال بالقائمة الجانبية بناءً على الموقع  الحالي
function setActiveMenu() {
    // تحديد الصفحة الحالية وإضافة كلاس اكتف للرابط المطابق
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll(".menu-link");

    if (!menuLinks.length) {
        return;
    }

    menuLinks.forEach(function (link) {
        const linkPath = new URL(link.href).pathname;

        if (linkPath === currentPath) {
            link.classList.add("active");
        }
    });
}

setActiveMenu();
// ==========================================================
