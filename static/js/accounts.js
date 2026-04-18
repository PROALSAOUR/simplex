// ============ دالة التحقق من صلاحية المعرف أثناء الكتابة ============
// تستخدم هذه الدالة للتحقق من صلاحية المعرف (اليوزرنيم) أثناء كتابة المستخدم له في نموذج التسجيل أو تعديل الحساب. تقوم بإرسال طلب إلى الخادم للتحقق مما إذا كان المعرف متاحًا أم لا، وتعرض رسالة للمستخدم بناءً على النتيجة.
// تستطيع التكيف مع حالتي الانشاء والتعديل وفقا لحالة تمرير currentUserId
let usernameTimeout = null;
function validateUsername(inputElement, feedback, url, currentUserId = null) {
    clearTimeout(usernameTimeout);
    const username = inputElement.value;

    feedback.innerText = "جاري التحقق...";
    feedback.style.color = "gray";

    return new Promise((resolve) => {
        usernameTimeout = setTimeout(() => {
            let requestUrl = `${url}?username=${username}`;
            if (currentUserId) {
                requestUrl += `&current_user_id=${currentUserId}`;
            }
            fetch(requestUrl)
                .then(response => response.json())
                .then(data => {
                    feedback.innerText = data.message;

                    if (data.status === 'success') {
                        feedback.style.color = 'green';
                        resolve(true);
                    } else {
                        feedback.style.color = 'red';
                        resolve(false);
                    }
                })
                .catch(() => {
                    feedback.innerText = "حدث خطأ";
                    feedback.style.color = "red";
                    resolve(false);
                });
        }, 500);
    });
}
//  ==========================================================
