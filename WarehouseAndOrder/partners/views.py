# from django.shortcuts import render
# Nơi viết hàm hoặc class xử lý request từ client
# Create your views here.
from rest_framework import viewsets # tạo các view api dựa trên các model đã có sẵn
from .models import Supplier, Customer
from .serializers import SupplierSerializer

class SupplierViewSet(viewsets.ModelViewSet):  # Bằng cách kế thừa từ ModelViewSet, lớp sẽ tự động được cung cấp một bộ "hành động" (actions) đầy đủ, tương ứng với các thao tác CRUD.
    queryset = Supplier.objects.all() # Truy vấn tất cả các đối tượng Supplier từ cơ sở dữ liệu.
    serializer_class = SupplierSerializer # Xác định lớp serializer sẽ được sử dụng để chuyển đổi dữ liệu giữa các đối tượng Supplier và định dạng JSON.


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

# === Template Views (Dùng cho các trang HTML) ===

@login_required
def customer_page(request):
    """Hiển thị danh sách tất cả khách hàng."""
    customers = Customer.objects.all()
    context = {'customers': customers}
    return render(request, 'customer.html', context)

@login_required
def add_customer(request):
    """Xử lý việc thêm khách hàng mới."""
    if request.method == 'POST':
        Customer.objects.create(
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
        )
        return redirect('partners:customer_page')
    return redirect('partners:customer_page')

@login_required
def edit_customer(request, customer_id):
    """Hiển thị form sửa và xử lý cập nhật khách hàng."""
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.name = request.POST.get('name')
        customer.phone = request.POST.get('phone')
        customer.email = request.POST.get('email')
        customer.address = request.POST.get('address')
        customer.save()
        return redirect('partners:customer_page')
    
    context = {'customer': customer}
    return render(request, 'edit_customer.html', context)

@login_required
def delete_customer(request, customer_id):
    """Xử lý việc xóa khách hàng."""
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        return redirect('partners:customer_page')
    return redirect('partners:customer_page')


@login_required
def supplier_page(request):
    """Hiển thị danh sách tất cả nhà cung cấp."""
    suppliers = Supplier.objects.all()
    context = {'suppliers': suppliers}
    return render(request, 'supplier.html', context)

@login_required
def add_supplier(request):
    """Xử lý việc thêm nhà cung cấp mới."""
    if request.method == 'POST':
        Supplier.objects.create(
            supplier_name=request.POST.get('name'), # Lưu ý tên trường là 'supplier_name'
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
        )
        return redirect('partners:supplier_page')
    # Nếu không phải POST thì không làm gì cả hoặc quay về trang supplier
    return redirect('partners:supplier_page')

@login_required
def edit_supplier(request, supplier_id):
    """Hiển thị form sửa và xử lý cập nhật nhà cung cấp."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        supplier.supplier_name = request.POST.get('name') # Lưu ý tên trường là 'supplier_name'
        supplier.phone = request.POST.get('phone')
        supplier.email = request.POST.get('email')
        supplier.address = request.POST.get('address')
        supplier.save()
        return redirect('partners:supplier_page')
    
    context = {'supplier': supplier}
    return render(request, 'edit_supplier.html', context)

@login_required
def delete_supplier(request, supplier_id):
    """Xử lý việc xóa nhà cung cấp."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        supplier.delete()
        return redirect('partners:supplier_page')
    # Chống xóa bằng GET request
    return redirect('partners:supplier_page')
