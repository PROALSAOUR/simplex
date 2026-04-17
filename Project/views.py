from django.shortcuts import render

def landing_page(request):
    """
    الدالة الرئيسية المسؤولة عن عرض صفحة الهبوط الرئيسية للمشروع 
    تم وضعها  هنا لأنها غير تابعة لأي من تطبيقات المشروع الأخرى 
    ولكي يتم اعطائها المسار الرئيسي في ملف الروابط الخاص بالمشروع
    (Project/urls.py)
    """
    
    return render(request, 'index.html')
    