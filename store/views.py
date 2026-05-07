from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction , models as db_models
from django.core.paginator import Paginator
import json

from Project.utils import compress_image
from accounts.decorators import vendor_only , advanced_permission_required
from store.validators import validate_image_file
from store.models import *
from store.forms import ProductRegisterForm

@login_required(login_url='accounts:log_in')
@vendor_only
def store_dashboard(request):
    return render(request, 'store/dashboard.html')

@login_required(login_url='accounts:log_in')
@vendor_only
def show_products(request):
    vendor = request.user.vendor
    products = vendor.store.products.all()

    # ── فلترة ──────────────────────────────────────────
    status = request.GET.get('status')
    if status in ['checking', 'approved', 'rejected']:
        products = products.filter(status=status)

    product_type = request.GET.get('type')
    if product_type in ['clothes', 'watches', 'Accessories']:
        products = products.filter(type=product_type)

    gender = request.GET.get('gender')
    if gender in ['male', 'female', 'unisex']:
        products = products.filter(gender=gender)

    show = request.GET.get('show')
    if show == 'true':
        products = products.filter(show=True)
    elif show == 'false':
        products = products.filter(show=False)

    offer = request.GET.get('offer')
    if offer == 'true':
        products = products.filter(offer=True)
    elif offer == 'false':
        products = products.filter(offer=False)

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    if price_min:
        try:
            products = products.filter(
                db_models.Q(offer=True, offer_price__gte=float(price_min)) |
                db_models.Q(offer=False, price__gte=float(price_min))
            )
        except ValueError:
            pass

    if price_max:
        try:
            products = products.filter(
                db_models.Q(offer=True, offer_price__lte=float(price_max)) |
                db_models.Q(offer=False, price__lte=float(price_max))
            )
        except ValueError:
            pass

    search = request.GET.get('search', '').strip()
    if search:
        products = products.filter(name__icontains=search)
    # ── ترتيب ──────────────────────────────────────────
    VALID_SORTS = {
        '-upload_at': '-upload_at',   # الأحدث أولاً
        'upload_at':  'upload_at',    # الأقدم أولاً
        'name':       'name',         # أبجدياً تصاعدي
        '-name':      '-name',        # أبجدياً تنازلي
        'price':      'price',        # الأرخص أولاً
        '-price':     '-price',       # الأغلى أولاً
    }
    selected_sort = request.GET.get('sort', '-upload_at')
    order_by = VALID_SORTS.get(selected_sort, '-upload_at')
    products = products.order_by(order_by)
    # ── Pagination ──────────────────────────────────────
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number if page_number else 1)
    except Exception:
        page_obj = paginator.page(1)

    # ── نبني query string بدون page لاستخدامه في روابط الباجنيتور ──
    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_string = query_params.urlencode()  # مثال: status=approved&gender=male

    context = {
        'page_obj': page_obj,
        'query_string': query_string,
        # قيم الفلاتر للحفاظ عليها في الـ form
        'selected_status': status or '',
        'selected_type': product_type or '',
        'selected_gender': gender or '',
        'selected_show': show or '',
        'selected_offer': offer or '',
        'price_min': request.GET.get('price_min', ''),
        'price_max': request.GET.get('price_max', ''),
        'search': search,
        'selected_sort':   selected_sort,
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

            # ── حفظ الألوان والمقاسات ──────────────────────────────
            colors_data = request.POST.get("colors_data")
            if colors_data:
                try:
                    colors_list = json.loads(colors_data)
                except (json.JSONDecodeError, ValueError):
                    colors_list = []

                for i, color_item in enumerate(colors_list):
                    image_file = request.FILES.get(f"color_image_{i}")
                    # ضغط الصورة إذا كانت موجودة
                    compressed_image = compress_image(image_file) if image_file else None
                    
                    color_obj = ProductColor.objects.create(
                        product=product,
                        color=color_item.get("color", ""),
                        available=color_item.get("available", True),
                        image=compressed_image
                    )

                    sizes_list = color_item.get("sizes", [])

                    #  المنتج دون مقاسات 
                    #  → لا تضف مقاسات للون حيث ان المقاس موحد 
                    if not sizes_list:
                        continue
                    else: # المنتج محددا مع مقاسات والمستخدم ضايف للألوان مقاسات
                        for size_item in sizes_list:
                            size_available = size_item.get("available", True)
                            if isinstance(size_available, str):
                                size_available = size_available.lower() in ['true', '1', 'yes']
                            else:
                                size_available = bool(size_available)

                            ProductSize.objects.create(
                                product_color=color_obj,
                                size=size_item.get("size", ""),
                                available=size_available
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
    
    if request.method == "POST":
        form = ProductRegisterForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()

            colors_data = request.POST.get("colors_data")
            if colors_data is not None:
                try:
                    colors_list = json.loads(colors_data)
                except (json.JSONDecodeError, ValueError):
                    colors_list = []

                processed_color_ids = []
                for i, color_item in enumerate(colors_list):
                    color_id = color_item.get('id')
                    image_file = request.FILES.get(f"color_image_{i}")

                    color_obj = None
                    if color_id:
                        color_obj = ProductColor.objects.filter(id=color_id, product=product).first()

                    if not color_obj:
                        color_obj = ProductColor(product=product)

                    color_obj.color = color_item.get('color', '')
                    available_value = color_item.get('available', True)
                    if isinstance(available_value, str):
                        color_obj.available = available_value.lower() in ['true', '1', 'yes']
                    else:
                        color_obj.available = bool(available_value)

                    if image_file:
                        compressed_image = compress_image(image_file)
                        if validate_image_file(compressed_image):
                            color_obj.image = compressed_image

                    color_obj.save()
                    processed_color_ids.append(color_obj.id)

                    color_obj.sizes.all().delete()
                    for size_item in color_item.get('sizes', []):
                        size_available = size_item.get('available', True)
                        if isinstance(size_available, str):
                            size_available = size_available.lower() in ['true', '1', 'yes']
                        else:
                            size_available = bool(size_available)

                        ProductSize.objects.create(
                            product_color=color_obj,
                            size=size_item.get('size', ''),
                            available=size_available,
                        )

                if processed_color_ids:
                    product.colors.exclude(id__in=processed_color_ids).delete()
                else:
                    product.colors.all().delete()

            messages.success(request, "تم تعديل المنتج بنجاح")
            return redirect('store:edit_product', pid=product.id)

    else:
        form = ProductRegisterForm(instance=product)
    
    colors_data = []
    for color in product.colors.prefetch_related('sizes').all():
        colors_data.append({
            'id': color.id,
            'color': color.color,
            'available': color.available,
            'imageURL': color.image.url if color.image else '',
            'imageName': color.image.name.split('/')[-1] if color.image else '',
            'sizes': [
                {
                    'size': size.size,
                    'available': size.available,
                }
                for size in color.sizes.all()
            ],
        })

    colors_data_json = json.dumps(colors_data, ensure_ascii=False)
    context = {
        'product': product,
        'edit_form': form,
        'product_images': product_images,
        'colors_data_json': colors_data_json,
    }
    return render(request, 'store/edit_product.html', context)

def view_product(request, pid):
    product = get_object_or_404(Product, id=pid)
    context = {
        'product': product,
    }
    return render(request, 'store/view_product.html', context)