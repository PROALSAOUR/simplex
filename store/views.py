from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.db import transaction , models as db_models
from django.core.paginator import Paginator
import hashlib, json

from Project.utils import compress_image
from accounts.decorators import vendor_only , advanced_permission_required
from store.validators import validate_image_file
from accounts.models import Vendor
from store.models import *
from store.forms import ProductRegisterForm

@login_required(login_url='accounts:log_in')
@vendor_only
def store_dashboard(request):
    #change-later قم بإنشاء دالة الداشبورد
    return render(request, 'store/dashboard.html')

@login_required(login_url='accounts:log_in')
@vendor_only
def show_products(request):
    """دالة عرض جميع المنتجات الخاصة بالمستخدم كما تحتوي على ألية البحث والفلترة """
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

    is_visible = request.GET.get('is_visible')
    if is_visible == 'true':
        products = products.filter(is_visible=True)
    elif is_visible == 'false':
        products = products.filter(is_visible=False)

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
        'selected_is_visible': is_visible or '',
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
    """الدالة المسؤولة عن صفحة اضافة منتج جديد """
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

                            ProductSize.objects.create(
                                product_color=color_obj,
                                size=size_item.get("size", ""),
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
@require_POST
def delete_product(request):
    "الدالة المسؤولة عن حذف منتج من المتجر, لايمكن الا لمالك المتجر او التحكم الكامل"
    if request.method == "POST":
        product_id  = request.POST.get('product_id')
        
        try:
            product_id = int(product_id)
            product =get_object_or_404(
                Product,
                id=product_id,
                store=request.user.vendor.store
            )
                
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
    
@login_required(login_url='accounts:log_in')
def edit_product(request, pid):
    """الدالة المسؤولة عن صفحة التعديل الخاصة بالمنتج"""
    product = get_object_or_404(Product, id=pid)
    product_images = product.images.all()
    
    # تحقق ان المستخدم بائع وان المنتج الذي يريد تعديله تابع لمتجره
    if  request.user.userprofile.user_type == 'vendor':
        if request.user.vendor.store != product.store :
            raise Http404("المنتج غير موجود")
        
    
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
                        ProductSize.objects.create(
                            product_color=color_obj,
                            size=size_item.get('size', ''),
                        )

                if processed_color_ids:
                    product.colors.exclude(id__in=processed_color_ids).delete()
                else:
                    product.colors.all().delete()

            # Handle images
            deleted_images = request.POST.get("deleted_images")
            if deleted_images:
                try:
                    deleted_ids = json.loads(deleted_images)
                    ProductImages.objects.filter(id__in=deleted_ids, product=product).delete()
                except (json.JSONDecodeError, ValueError):
                    deleted_ids = []
            else:
                deleted_ids = []

            order_data = request.POST.get("images_order")
            if order_data:
                try:
                    order_list = json.loads(order_data)
                    images = request.FILES.getlist("images")
                    images_map = {img.name: img for img in images}

                    existing_hashes = set()
                    for existing in product.images.all():
                        try:
                            existing.image.open()
                            file_bytes = existing.image.read()
                            existing_hashes.add(hashlib.md5(file_bytes).hexdigest())
                            existing.image.close()
                        except Exception:
                            pass

                    for item in order_list:
                        image_id = item.get("id")
                        image_name = item.get("name")
                        priority = item.get("index")
                        is_existing = item.get("isExisting", False)

                        if is_existing and image_id:
                            # Update priority for existing image
                            ProductImages.objects.filter(id=image_id, product=product).update(priority=priority)
                        elif not is_existing:
                            # Add new image if not duplicate by content
                            image_file = images_map.get(image_name)
                            if image_file and validate_image_file(image_file):
                                image_file.seek(0)
                                uploaded_hash = hashlib.md5(image_file.read()).hexdigest()
                                image_file.seek(0)
                                if uploaded_hash in existing_hashes:
                                    continue
                                compressed_image = compress_image(image_file)
                                ProductImages.objects.create(
                                    product=product,
                                    image=compressed_image,
                                    priority=priority
                                )
                except (json.JSONDecodeError, ValueError):
                    pass

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
                }
                for size in color.sizes.all()
            ],
        })

    colors_data_json = json.dumps(colors_data, ensure_ascii=False)
    
    images_data = []
    for image in product_images:
        images_data.append({
            'id': image.id,
            'url': image.image.url,
            'name': image.image.name.split('/')[-1],
            'size': image.image.size,
            'priority': image.priority,
        })

    images_data_json = json.dumps(images_data, ensure_ascii=False)
    context = {
        'product': product,
        'edit_form': form,
        'product_images': product_images,
        'colors_data_json': colors_data_json,
        'images_data_json': images_data_json,
    }
    return render(request, 'store/edit_product.html', context)

def view_product(request, pid):
    """الدالة المسؤولة عن عرض صفحة المنتج للزبون ليتمكن من اجراء عملية الشراء منها"""
    product = get_object_or_404(Product, id=pid)
    product_images = product.images.all()
    colors = product.colors.filter(available=True).prefetch_related('sizes')
    is_product_owner = False
    if request.user.is_authenticated:
        try:
            is_product_owner = request.user.vendor.store == product.store
        except Vendor.DoesNotExist:
            pass
    # [يعرض المنتج دائما للبائع لكن مع الاخطاء الخاصة به] [لعرض المنتج: [للزبون يجب ان يكون موافق عليه من الادارة ومعروض من البائع 
    can_view = is_product_owner or (product.is_visible and product.status == "approved")

    context = {
        'product': product,
        'is_product_owner': is_product_owner,
        "can_view": can_view,
        'product_images': product_images,
        'colors': colors,
        'product_price': str(product.get_price()),
    }
    return render(request, 'store/view_product.html', context)
