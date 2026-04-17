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
