from django.shortcuts import render

def show_products(request):
    # جلب المستخدم
    vendor = request.user.vendor
    # جلب المتجر المرتبط بالمستخدم
    store = vendor.store
    # جلب المنتجات المرتبطة بالمتجر
    products = store.products.all()
    # تمرير المنتجات إلى القالب لعرضها
    context = {
        'products': products
    }
    return render(request, 'index.html', context)