// الكود والدوال المسؤولة عن قوائم الفلترة والترتيب
function toggleMenu(button, targetSelector, closeOnOutsideClick = false) {
    // فتح أو إغلاق القائمة المرتبطة بالزر
    const target = document.querySelector(targetSelector);

    if (!button || !target) return;

    button.classList.toggle("open");
    target.classList.toggle("open");

    if (closeOnOutsideClick && target.classList.contains("open")) {
        setTimeout(() => {
            document.addEventListener("click", function closeMenu(event) {
                if (
                    !target.contains(event.target) &&
                    !button.contains(event.target)
                ) {
                    button.classList.remove("open");
                    target.classList.remove("open");

                    document.removeEventListener("click", closeMenu);
                }
            });
        }, 0);
    }
}
// =========================================================================
// الكود والدوال المسؤولة عن قائمة زر الاكشن منيو داخل الجدول
const menu = document.getElementById("action-menu");
// إذا كانت القائمة غير موجودة في الصفحة، أوقف الكود بدون أخطاء
if (menu) {
    
    const GAP = 3;
    const PADDING = 7;
    let activeTrigger = null;
    let activeRow = null;

    function computePosition(triggerRect, menuEl) {
        menuEl.style.top = "-9999px";
        menuEl.style.left = "-9999px";
        const menuRect = menuEl.getBoundingClientRect();
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        let viewportTop = triggerRect.bottom + GAP;
        let viewportLeft = triggerRect.left;
        if (viewportLeft + menuRect.width > vw - PADDING) {
            viewportLeft = vw - PADDING - menuRect.width;
        }
        if (viewportLeft < PADDING) {
            viewportLeft = PADDING;
        }
        if (viewportTop + menuRect.height > vh - PADDING) {
            viewportTop = vh - PADDING - menuRect.height;
        }
        if (viewportTop < PADDING) {
            viewportTop = PADDING;
        }
        return {
            top: viewportTop + window.scrollY,
            left: viewportLeft + window.scrollX
        };
    }

    function openActionMenu(trigger) {

        activeTrigger = trigger;
        activeRow = trigger.closest("tr");

        // الحصول على عناصر القائمة 
        const viewBtn = menu.querySelector("#view-btn"); 
        const editBtn = menu.querySelector("#edit-btn"); 
        const deleteBtn = menu.querySelector("#delete-btn");

        // البيانات الموجودة في زر الإجراءات 
        const id = trigger.dataset.id; 
        const name = trigger.dataset.name; 
        const viewUrl = trigger.dataset.viewUrl; 
        const editUrl = trigger.dataset.editUrl; 
        
        // تحديث رابط العرض 
        if (viewBtn) { viewBtn.href = viewUrl || "#"; } 
        // تحديث رابط التعديل 
        if (editBtn) { editBtn.href = editUrl || "#"; } 
        // تحديث بيانات الحذف 
        if (deleteBtn) { deleteBtn.dataset.id = id || ""; deleteBtn.dataset.name = name || ""; }


        trigger.classList.add("open");
        trigger.setAttribute("aria-expanded", "true");

        const rect = trigger.getBoundingClientRect();

        const { top, left } = computePosition(rect, menu);

        menu.style.top = `${top}px`;
        menu.style.left = `${left}px`;

        menu.classList.add("open");
    }

    function closeActionMenu() {

        if (activeTrigger) {
            activeTrigger.classList.remove("open");
            activeTrigger.setAttribute("aria-expanded", "false");
        }

        menu.classList.remove("open");

        activeTrigger = null;
        activeRow = null;
    }

    // النقر على الزر المسؤول عن فتح القائمة
    document.addEventListener("click", (e) => {

        const trigger = e.target.closest(".td-actions");
        // إذا تم الضغط على زر الإجراءات
        if (trigger) {

            const isSameTrigger = trigger === activeTrigger;

            closeActionMenu();
            // إذا كان نفس الزر، يبقى مغلقاً
            if (!isSameTrigger) {
                openActionMenu(trigger);
            }
            return;
        }
        // أي مكان آخر في الصفحة يغلق القائمة الا النقر على القائمة نفسها
        if (!e.target.closest("#action-menu")) closeActionMenu();
    });
    // تغيير حجم الشاشة يغلق القائمة
    window.addEventListener("resize", () => {
        closeActionMenu();
    });
    // زر Escape يغلق القائمة
    document.addEventListener("keydown", (e) => {

        if (e.key === "Escape") {
            closeActionMenu();
        }

    });
}
// =========================================================================
// دوال خاصة بالفلترة والترتيب داخل الجدول

function applySort(val) {
    /* ── Apply sort value then submit ── */
    document.getElementById('sort-input').value = val;
    document.getElementById('sort-menu').classList.remove('open');
    document.getElementById('search-form').submit();
}
function clearParam(name) {
    /* ── Remove a single filter chip and re-submit ── */
    const url    = new URL(window.location.href);
    const names  = name.split(';');
    names.forEach(n => url.searchParams.delete(n.trim()));
    url.searchParams.delete('page');
    window.location.href = url.toString();
}
// =========================================================================
// دوال خاصة بالنقر على الصفوف داخل الجدول للانتقال إلى صفحة العرض الخاصة بالصف
document.addEventListener('DOMContentLoaded', function () {
    const rows = document.querySelectorAll('tr[data-view-url]');

    rows.forEach(function (row) {

        row.addEventListener('click', function (e) {
            // تجاهل النقر إذا كان المستخدم قد حدد نصًا (مثلاً لنسخ اسم المنتج)
            if (window.getSelection().toString().length > 0) {
                return;
            }

            // تجاهل النقر إذا كان على زر الإجراءات أو داخل القائمة المنسدلة
            if (e.target.closest('.td-actions') || e.target.closest('.action-menu')) {
                return;
            }

            const url = row.dataset.viewUrl;
            if (url) {
                window.location.href = url;
            }
        });
    });
});
// =========================================================================
