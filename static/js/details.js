function rememberDetailsState() {
    const detailsElements = document.querySelectorAll("details");

    if (!detailsElements.length) {
        return;
    }

    const pageKey = `details-state-${window.location.pathname}`;

    detailsElements.forEach(function (details, index) {
        const key = details.id || index;
        const storageKey = `${pageKey}-${key}`;

        // استرجاع الحالة المحفوظة لهذه الصفحة
        const savedState = sessionStorage.getItem(storageKey);

        if (savedState !== null) {
            details.open = savedState === "open";
        }

        // حفظ الحالة عند فتح أو إغلاق القسم
        details.addEventListener("toggle", function () {
            sessionStorage.setItem(
                storageKey,
                details.open ? "open" : "closed"
            );
        });
    });
    
}

rememberDetailsState();