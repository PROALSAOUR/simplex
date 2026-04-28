from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import vendor_only , advanced_permission_required
from store.forms import ProductRegisterForm
from django.http import JsonResponse
from .models import Product


@login_required(login_url='accounts:log_in')
@vendor_only
def store_dashboard(request):
    return render(request, 'store/dashboard.html')

@login_required(login_url='accounts:log_in')
@vendor_only
def show_products(request):
    """دالة وظيفتها عرض جميع المنتجات الخاصة بالمستخدم"""
    vendor = request.user.vendor
    products = vendor.store.products.all()
    context = {
        'products': products
    }
    return render(request, 'store/products.html', context)

@login_required(login_url='accounts:log_in')
@vendor_only
def add_product(request):
    """دالة وظيفتها اضافة منتج جديد """
    store = request.user.vendor.store
    if request.method == "POST":
        form = ProductRegisterForm(request.POST, request.FILES, store=store)
        if form.is_valid():
            form.save() 
            return redirect('store:show_products')
        else:
            print(form.errors)
            # إعادة عرض النموذج مع الأخطاء
            context = {"add_form": form}
            return render(request, 'store/add_product.html', context)
     
    add_form = ProductRegisterForm()
    context = {
        "add_form": add_form,
    }
    return render(request, 'store/add_product.html', context)

@login_required(login_url='accounts:log_in')
@vendor_only
@advanced_permission_required()
def delete_product(request):
    "الدالة المسؤولة عن حذف منتج من المتجر, لايمكن الا لمالك المتجر او التحكم الكامل"
    if request.method == "POST":
        product_id  = request.POST.get('product_id')
        store = request.user.vendor.store
        
        try:
            product_id = int(product_id)
            product = Product.objects.get(id=product_id)
            # لو المتجر الخاص بالمنتج مو نفس التجر الخاص بالمستخدم لا تحذف المنتج ورجع خطأ
            if product.store != store :
                return JsonResponse({
                    "status": "error",
                    "message":'عذراً, يبدو انك  تحاول حذف منتج لا ينتمي الى متجرك!'
                })
                
            product.delete()
            return JsonResponse({
            "status": "success",
            "message": 'تم حذف المنتج بنجاح'
            })
        except Exception as e:
            return JsonResponse({
            "status": "error",
            "message": str(e)
        })
    
    else:
        return JsonResponse({"status": "error", "message": "طلب غير صالح"})

@login_required(login_url='accounts:log_in')
@vendor_only
def edit_product(request, pid):
    product = get_object_or_404(Product, id=pid)
    
    
    context = {
        'product': product,
    }
    return render(request, 'store/edit_product.html', context)