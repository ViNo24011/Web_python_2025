from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages
from django.db.models import ProtectedError # Để xử lý lỗi khi xóa kho có sản phẩm liên kết
from django.contrib.auth.decorators import login_required
from .models import Product, Warehouse

@login_required
def select_warehouse(request):
    
    warehouses_list = Warehouse.objects.all().order_by('name')
    context = {
        'warehouses_list': warehouses_list
    }
    return render(request, 'select_warehouse.html', context) # Hiển thị danh sách kho để chọn
    # render(request, template_name, context=None, content_type=None, status=None, using=None)


@login_required
def product_list_by_warehouse(request, warehouse_id):
    
    selected_warehouse = get_object_or_404(Warehouse, id=warehouse_id) 
    products = Product.objects.filter(warehouse=selected_warehouse).select_related('warehouse').order_by('name')
    # Lấy tất cả kho để dùng cho modal "Thêm" (nếu cần dropdown)
    all_warehouses = Warehouse.objects.all().order_by('name')

    context = {
        'products': products,
        'selected_warehouse': selected_warehouse, # Kho đang xem
        'warehouses': all_warehouses # Cho modal thêm sản phẩm
    }
    
    storage = messages.get_messages(request)
    if storage:
        context['messages'] = storage
    return render(request, 'product.html', context)


@login_required
def add_product_to_warehouse(request, warehouse_id):
    """
    Xử lý việc thêm sản phẩm mới vào kho đã chọn.
    """
    selected_warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        category_name = request.POST.get('category_name')
        unit = request.POST.get('unit')
        price_str = request.POST.get('price')
        quantity_str = request.POST.get('quantity')
        min_quantity_str = request.POST.get('min_quantity')

        
        if not all([name, category_name, unit, price_str, quantity_str, min_quantity_str]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc.')
        else:
            try:
                
                price = float(price_str) 
                quantity = int(quantity_str)
                min_quantity = int(min_quantity_str)

                Product.objects.create(
                    name=name,
                    category_name=category_name,
                    unit=unit,
                    price=price,
                    quantity=quantity,
                    min_quantity=min_quantity,
                    warehouse=selected_warehouse 
                )
                messages.success(request, f'Đã thêm sản phẩm "{name}" vào kho "{selected_warehouse.name}".')
            except ValueError:
                 messages.error(request, 'Giá nhập, số lượng và lượng cảnh báo phải là số hợp lệ.')
            except Exception as e:
                messages.error(request, f'Lỗi khi thêm sản phẩm: {e}')

        return redirect('inventory:product_list_by_warehouse', warehouse_id=warehouse_id)

    
    return redirect('inventory:select_warehouse')


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    warehouse_id_to_redirect = product.warehouse_id
    product_name = product.name

    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, f'Đã xóa sản phẩm "{product_name}".')
        except Exception as e:
            messages.error(request, f'Lỗi khi xóa sản phẩm: {e}')
        if warehouse_id_to_redirect:
             return redirect('inventory:product_list_by_warehouse', warehouse_id=warehouse_id_to_redirect)
        else:
             return redirect('inventory:select_warehouse')
    # nếu không phải POST (ấn hủy thay vì xác nhận), chuyển hướng về danh sách sản phẩm
    if warehouse_id_to_redirect:
        return redirect('inventory:product_list_by_warehouse', warehouse_id=warehouse_id_to_redirect)
    else:
        return redirect('inventory:select_warehouse')

@login_required
def edit_product(request, product_id):
    """ Displays the edit product form (GET) and handles updates (POST). """
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Get data from form
        name = request.POST.get('name')
        category_name = request.POST.get('category_name')
        unit = request.POST.get('unit')
        price_str = request.POST.get('price')
        quantity_str = request.POST.get('quantity')
        min_quantity_str = request.POST.get('min_quantity')
        new_warehouse_id = request.POST.get('warehouse_id') # Allow changing warehouse

        if not all([name, category_name, unit, price_str, quantity_str, min_quantity_str]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc.')
        else:
            try:
              
                product.name = name
                product.category_name = category_name
                product.unit = unit
                product.price = float(price_str) 
                product.quantity = int(quantity_str) 
                product.min_quantity = int(min_quantity_str) 

                # Update warehouse
                new_warehouse_instance = None
                if new_warehouse_id: # If a warehouse is selected
                    try:
                        new_warehouse_instance = Warehouse.objects.get(id=new_warehouse_id)
                    except Warehouse.DoesNotExist:
                        messages.warning(request, f'ID kho "{new_warehouse_id}" không hợp lệ. Kho hàng không được thay đổi.')
                        new_warehouse_instance = product.warehouse 
                product.warehouse = new_warehouse_instance 
                product.save()
                messages.success(request, f'Đã cập nhật sản phẩm "{product.name}".')
                current_warehouse_id = product.warehouse_id
                if current_warehouse_id:
                    return redirect('inventory:product_list_by_warehouse', warehouse_id=current_warehouse_id)
                else:
                    return redirect('inventory:select_warehouse')

            except ValueError:
                 messages.error(request, 'Giá nhập, số lượng và lượng cảnh báo phải là số hợp lệ.')
            except Exception as e:
                messages.error(request, f'Lỗi khi cập nhật sản phẩm: {e}')

    warehouses = Warehouse.objects.all().order_by('name') 
    context = {
        'product': product,
        'warehouses': warehouses
    }

    storage = messages.get_messages(request)
    if storage:
        context['messages'] = storage
    return render(request, 'edit_product.html', context) # Hiển thị form chỉnh sửa sản phẩm

@login_required
def warehouse_page(request):
    warehouses = Warehouse.objects.all().order_by('name')
    context = {'warehouses': warehouses}
    storage = messages.get_messages(request) # Lấy tin nhắn từ hệ thống từ trước
    if storage:
        context['messages'] = storage
    return render(request, 'warehouse.html', context)

@login_required
def add_warehouse(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        if Warehouse.objects.filter(name__iexact=name).exists():
             messages.error(request, f'Lỗi: Tên kho "{name}" đã tồn tại.')
        elif name and location:
            Warehouse.objects.create(name=name, location=location)
            messages.success(request, 'Thêm kho hàng mới thành công.')
        else:
            messages.error(request, 'Tên kho và địa chỉ không được để trống.')
    return redirect('inventory:warehouse_page')

@login_required
def edit_warehouse(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        if Warehouse.objects.filter(name__iexact=name).exclude(id=warehouse_id).exists():
            messages.error(request, f'Lỗi: Tên kho "{name}" đã tồn tại.')
            storage = messages.get_messages(request)
            for message in storage: messages.error(request, message)
            return redirect('inventory:edit_warehouse', warehouse_id=warehouse_id)
        elif name and location:
            warehouse.name = name
            warehouse.location = location
            warehouse.save()
            messages.success(request, 'Cập nhật kho hàng thành công.')
            return redirect('inventory:warehouse_page')
        else:
            messages.error(request, 'Tên kho và địa chỉ không được để trống.')
             
            storage = messages.get_messages(request)
            for message in storage: messages.error(request, message)
            return redirect('inventory:edit_warehouse', warehouse_id=warehouse_id)

    # GET request
    context = {'warehouse': warehouse}
    storage = messages.get_messages(request)
    if storage:
        context['messages'] = storage
    return render(request, 'edit_warehouse.html', context)

@login_required
def delete_warehouse(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    if request.method == 'POST':
        try:
            warehouse_name = warehouse.name
            warehouse.delete()
            messages.success(request, f'Đã xóa kho hàng "{warehouse_name}".')
        except ProtectedError:
            messages.error(request, f'Không thể xóa kho "{warehouse.name}" vì vẫn còn sản phẩm liên kết.')
    return redirect('inventory:warehouse_page')
