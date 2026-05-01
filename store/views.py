import json
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import vendor_only , advanced_permission_required
from store.forms import ProductRegisterForm
from django.http import JsonResponse
from django.contrib import messages
from store.validators import validate_image_file
from .models import Product, ProductImages
from django.db import transaction

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
    return render(request, 'store/show_products.html', context)

@login_required(login_url='accounts:log_in')
@vendor_only
@transaction.atomic # تجعل كل العمليات داخل الدالة تُنفَّذ كحزمة واحدة، إذا حدث خطأ في أي خطوة يتم التراجع عن كل العمليات السابقة
def add_product(request):
    """دالة وظيفتها اضافة منتج جديد """
    store = request.user.vendor.store
    if request.method == "POST":
        form = ProductRegisterForm(request.POST, request.FILES, store=store)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            
            order_data = request.POST.get("images_order")
            order_data = json.loads(order_data) if order_data else []
            
            images = request.FILES.getlist("images")
            images_map = {img.name: img for img in images} # نحول الصور لقاموس (اسم → ملف)
            for item in order_data:
                image_name = item.get("name")
                priority = item.get("index")
                image_file = images_map.get(image_name)
                
                if not image_file:  # تخطي إذا لم يتم العثور على الملف
                    continue 
                
                if not validate_image_file(image_file):
                    continue  # تخطي الصورة إذا لم تكن صالحة    
                
                ProductImages.objects.create(
                    product=product,
                    image=image_file,
                    priority=priority
                )
            
            messages.success(request, "تمت إضافة المنتج بنجاح")
            return redirect('store:show_products')
        else:
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
    product_images = product.images.all()
    
    context = {
        'product': product,
        'product_images': product_images,
    }
    return render(request, 'store/edit_product.html', context)