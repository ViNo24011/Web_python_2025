from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer

# === API Views ===
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer

# === Template Views ===
@login_required
def product_page(request):
    # 1. Lấy tất cả sản phẩm từ database
    products = Product.objects.all()
    
    # 2. Đóng gói danh sách products vào một dictionary tên là context
    context = {
        'products': products
    }
    
    # 3. Gửi context đến template khi render
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

        # Tạo một đối tượng Product mới và lưu vào database
        Product.objects.create(
            name=name,
            category_name=category_name,
            unit=unit,
            price=price,
            quantity=quantity,
            min_quantity=min_quantity
        )
        # Sau khi lưu, chuyển hướng người dùng về lại trang danh sách sản phẩm
        return redirect('inventory:product_page')

    # Nếu không phải POST, cứ quay về trang sản phẩm
    return redirect('inventory:product_page')

# Thêm hàm mới để xóa sản phẩm
@login_required
def delete_product(request, product_id):
    # Lấy sản phẩm cần xóa, nếu không tìm thấy sẽ báo lỗi 404
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST': # Chỉ thực hiện xóa nếu là request POST để tăng bảo mật
        product.delete()
        return redirect('inventory:product_page')
    
    # Nếu là GET request, có thể hiển thị trang xác nhận (ở đây ta bỏ qua cho đơn giản)
    return redirect('inventory:product_page')

# inventory/views.py
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
        product.save() # Lưu thay đổi
        return redirect('inventory:product_page')

    # Nếu là request GET, hiển thị form với dữ liệu đã có
    context = {
        'product': product
    }
    # Chúng ta sẽ tạo một template mới là edit_product.html
    return render(request, 'edit_product.html', context)