//  ========================================================================
// دالة التحقق من صلاحية المعرف أثناء الكتابة 
// تستخدم هذه الدالة للتحقق من صلاحية المعرف (اليوزرنيم) أثناء كتابة المستخدم له في نموذج التسجيل أو تعديل الحساب. تقوم بإرسال طلب إلى الخادم للتحقق مما إذا كان المعرف متاحًا أم لا، وتعرض رسالة للمستخدم بناءً على النتيجة.
// تستطيع التكيف مع حالتي الانشاء والتعديل وفقا لحالة تمرير currentUserId
let usernameTimeout = null;
async function validateUsername(inputElement, feedback, url, currentUserId = null) {
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
                    feedback.innerText = Array.isArray(data.message)
                    ? data.message.join(" ")
                    : data.message;

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
//  =========================================================================
//  دالة التحقق من صلاحية رقم الهاتف أثناء الكتابة 
let phonenumberTimeout = null;
let phoneValidationRequestId = 0;
async function validatePhoneNumber(inputElement, feedback, url) {
    clearTimeout(phonenumberTimeout);

    const phoneNumber = inputElement.value.trim();
    const requestId = ++phoneValidationRequestId;

    if (!phoneNumber) {
        feedback.innerText = "أدخل رقم الهاتف .";
        feedback.style.color = "gray";
        return false;
    }

    feedback.innerText = "جاري التحقق...";
    feedback.style.color = "gray";

    return new Promise((resolve) => {
        phonenumberTimeout = setTimeout(async () => {
            try {
                const requestUrl =
                    `${url}?phone_number=${encodeURIComponent(phoneNumber)}`;

                const response = await fetch(requestUrl);
                const data = await response.json();

                // تجاهل نتائج الطلبات القديمة.
                if (requestId !== phoneValidationRequestId) {
                    resolve(false);
                    return;
                }

                feedback.innerText = data.message;

                const isValid =
                    response.ok && data.status === "success";

                feedback.style.color = isValid ? "green" : "red";

                resolve(isValid);

            } catch (error) {
                if (requestId === phoneValidationRequestId) {
                    feedback.innerText =
                        "تعذر التحقق من رقم الهاتف.";

                    feedback.style.color = "red";
                }

                resolve(false);
            }
        }, 500);
    });
}
//  =========================================================================
