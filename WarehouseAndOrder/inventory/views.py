from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import ProtectedError
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import Product, Warehouse
from .serializers import ProductSerializer

# === API Views ===
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer

# === Template Views ===
# views.py (Đã sửa)
@login_required
def product_page(request):
    products = Product.objects.select_related('warehouse').all()
    warehouses = Warehouse.objects.all()
    
    context = {
        'products': products,
        'warehouses': warehouses  
    }
    
    return render(request, 'product.html', context)

@login_required
def add_product(request):
    # Chỉ xử lý nếu phương thức là POST
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        name = request.POST.get('name')
        category_name = request.POST.get('category_name')
        unit = request.POST.get('unit')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        min_quantity = request.POST.get('min_quantity')

        # --- PHẦN THÊM MỚI ---
        # Lấy ID kho hàng từ form
        warehouse_id = request.POST.get('warehouse_id')
        
        warehouse_instance = None
        # Kiểm tra nếu người dùng có chọn kho (ID không rỗng)
        if warehouse_id:
            try:
                # Lấy đối tượng kho hàng từ ID
                warehouse_instance = Warehouse.objects.get(id=warehouse_id)
            except Warehouse.DoesNotExist:
                warehouse_instance = None # An toàn nếu ID không hợp lệ
        # --- HẾT PHẦN THÊM MỚI ---

        # Tạo một đối tượng Product mới và lưu vào database
        Product.objects.create(
            name=name,
            category_name=category_name,
            unit=unit,
            price=price,
            quantity=quantity,
            min_quantity=min_quantity,
            warehouse=warehouse_instance  # <-- GÁN KHO HÀNG VÀO ĐÂY
        )
        # Sau khi lưu, chuyển hướng người dùng về lại trang danh sách sản phẩm
        return redirect('inventory:product_page')

    return redirect('inventory:product_page')


@login_required
def delete_product(request, product_id):
    # (Hàm này không cần thay đổi)
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST': 
        product.delete()
        return redirect('inventory:product_page')
    
    return redirect('inventory:product_page')


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Lấy dữ liệu từ form và cập nhật cho sản phẩm
        product.name = request.POST.get('name')
        product.category_name = request.POST.get('category_name')
        product.unit = request.POST.get('unit')
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        product.min_quantity = request.POST.get('min_quantity')
        
        # --- PHẦN THÊM MỚI ---
        # Lấy ID kho hàng từ form
        warehouse_id = request.POST.get('warehouse_id')

        warehouse_instance = None
        if warehouse_id:
            try:
                warehouse_instance = Warehouse.objects.get(id=warehouse_id)
            except Warehouse.DoesNotExist:
                warehouse_instance = None
        
        product.warehouse = warehouse_instance # <-- CẬP NHẬT KHO HÀNG
        # --- HẾT PHẦN THÊM MỚI ---
        
        product.save() # Lưu thay đổi
        return redirect('inventory:product_page')

    # --- PHẦN GET ĐÃ SỬA ---
    # Nếu là request GET, hiển thị form với dữ liệu đã có
    # Lấy TẤT CẢ kho hàng để hiển thị trong dropdown
    warehouses = Warehouse.objects.all()

    context = {
        'product': product,
        'warehouses': warehouses  # <-- GỬI DANH SÁCH KHO CHO TEMPLATE
    }
    # Chúng ta sẽ tạo một template mới là edit_product.html
    return render(request, 'edit_product.html', context)

# === CÁC VIEW MỚI CHO KHO HÀNG (Warehouse) ===
@login_required
def warehouse_page(request):
    """
    Hiển thị danh sách kho hàng.
    Form thêm kho được tích hợp qua modal, nên view này
    cũng xử lý việc hiển thị thông báo lỗi/thành công.
    """
    warehouses = Warehouse.objects.all()
    context = {
        'warehouses': warehouses
    }
    return render(request, 'warehouse.html', context)

@login_required
def add_warehouse(request):
    """
    Chỉ xử lý POST request từ modal 'Thêm kho'.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')

        if name and location:
            Warehouse.objects.create(name=name, location=location)
            messages.success(request, 'Thêm kho hàng mới thành công.')
        else:
            messages.error(request, 'Tên kho và địa chỉ không được để trống.')
            
    return redirect('inventory:warehouse_page')

@login_required
def edit_warehouse(request, warehouse_id):
    """
    Hiển thị trang sửa kho (GET) và xử lý cập nhật (POST).
    """
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        
        if name and location:
            warehouse.name = name
            warehouse.location = location
            warehouse.save()
            messages.success(request, 'Cập nhật kho hàng thành công.')
            return redirect('inventory:warehouse_page')
        else:
            messages.error(request, 'Tên kho và địa chỉ không được để trống.')
            # Quay lại trang edit nếu lỗi
            return redirect('inventory:edit_warehouse', warehouse_id=warehouse_id)

    # Nếu là GET request
    context = {
        'warehouse': warehouse
    }
    return render(request, 'edit_warehouse.html', context)

@login_required
def delete_warehouse(request, warehouse_id):
    """
    Xử lý xóa kho hàng. Chỉ cho phép xóa nếu không còn
    sản phẩm nào liên kết (do on_delete=models.PROTECT).
    """
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    if request.method == 'POST':
        try:
            warehouse.delete()
            messages.success(request, f'Đã xóa kho hàng "{warehouse.name}".')
        except ProtectedError:
            # Bắt lỗi nếu vẫn còn sản phẩm trong kho
            messages.error(request, f'Không thể xóa kho "{warehouse.name}" vì vẫn còn sản phẩm liên kết.')
    
    return redirect('inventory:warehouse_page')