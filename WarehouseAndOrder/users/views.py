from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # Để bỏ qua CSRF cho API login
from django.contrib import messages
import json
from inventory.models import Product, Warehouse
from partners.models import Customer
from transactions.models import ExportReceipt
from rest_framework import viewsets
from rest_framework.permissions import BasePermission # Để tạo custom permission
from .models import User
from .serializers import UserSerializer

# --- Custom Permission Class  ---
class IsManagerUser(BasePermission):
    """
    Custom permission để chỉ cho phép user có username là 'manager'
    mới có quyền truy cập view này (CRUD User).
    """
    def has_permission(self, request, view):
        # Kiểm tra xem user đã đăng nhập VÀ username của họ có phải là 'manager' không
        return request.user and request.user.is_authenticated and request.user.username == 'manager'

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsManagerUser]

# --- Views xác thực ---
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password) # Xác thực người dùng
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful', 'username': user.username})
        else:
            return JsonResponse({'message': 'Invalid credentials'}, status=401)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def login_page(request):
    return render(request, 'login.html')

def forget_page(request):
    return render(request, 'forget.html')

def logout_view(request):
    logout(request)
    return redirect('users:login_page')

# --- View trang chủ  ---
@login_required
def home_page(request):
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    total_orders = ExportReceipt.objects.count()
    total_warehouses = Warehouse.objects.count()

    warehouses = Warehouse.objects.prefetch_related(
        models.Prefetch(
            'products',
            queryset=Product.objects.filter(quantity__lte=models.F('min_quantity')), # Sản phẩm sắp hết hàng
            to_attr='low_stock_products_in_warehouse' # Lưu trữ kết quả truy vấn vào thuộc tính sắp hết hàng
        )
    ).all()

    warehouses_with_low_stock = [
        wh for wh in warehouses if hasattr(wh, 'low_stock_products_in_warehouse') and wh.low_stock_products_in_warehouse
    ]
    
    products_nearing_out_of_stock = sum(len(wh.low_stock_products_in_warehouse) for wh in warehouses_with_low_stock)

    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_warehouses': total_warehouses,
        'warehouses_with_low_stock': warehouses_with_low_stock,
        'products_nearing_out_of_stock': products_nearing_out_of_stock
    }
    return render(request, 'home.html', context)

@login_required
def user_list_page(request):
    """
    Hiển thị trang quản lý người dùng (Read - List).
    """
    # Chỉ manager mới thấy trang này (Giả định 'manager' có is_staff=True)
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('users:home_page')
        
    users = User.objects.all().order_by('id')
    return render(request, 'user_management.html', {'users': users})

@login_required
def add_user(request):
    """
    Xử lý thêm người dùng mới (Create).
    """
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
        return redirect('user_list_page')

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Lấy giá trị checkbox
        is_active = 'is_active' in request.POST
        is_staff = 'is_staff' in request.POST
        is_superuser = 'is_superuser' in request.POST

        if not username or not password or not password2:
            messages.error(request, 'Tên đăng nhập và mật khẩu là bắt buộc.')
            return redirect('users:user_list_page')

        if password != password2:
            messages.error(request, 'Hai mật khẩu không khớp.')
            return redirect('users:user_list_page')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập này đã tồn tại.')
            return redirect('users:user_list_page')
        
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'Email này đã tồn tại.')
            return redirect('users:user_list_page')
        
        # --- Tạo User ---
        try:
            # Dùng create_user để hash mật khẩu tự động
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Cập nhật các quyền
            user.is_active = is_active
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
            
            messages.success(request, f'Tạo người dùng {username} thành công!')
        
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {e}')

    return redirect('users:user_list_page')

@login_required
def edit_user(request, user_id):
    """
    Hiển thị trang sửa và xử lý cập nhật người dùng (Update).
    """
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('home_page')

    user_obj = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        user_obj.email = request.POST.get('email', '')
        user_obj.first_name = request.POST.get('first_name', '')
        user_obj.last_name = request.POST.get('last_name', '')
        
        # Lấy giá trị checkbox
        user_obj.is_active = 'is_active' in request.POST
        user_obj.is_staff = 'is_staff' in request.POST
        user_obj.is_superuser = 'is_superuser' in request.POST

        # Không cho phép manager tự tước quyền staff của mình
        if request.user.id == user_obj.id and not user_obj.is_staff:
            messages.error(request, 'Bạn không thể tự tước quyền Manager của mình.')
        else:
            try:
                user_obj.save()
                messages.success(request, f'Cập nhật người dùng {user_obj.username} thành công!')
                
                # Mật khẩu (nếu được cung cấp)
                password = request.POST.get('password')
                password2 = request.POST.get('password2')
                if password:
                    if password == password2:
                        user_obj.set_password(password)
                        user_obj.save()
                        messages.success(request, f'Đã cập nhật mật khẩu cho {user_obj.username}.')
                    else:
                        messages.error(request, 'Cập nhật mật khẩu thất bại: Hai mật khẩu không khớp.')

            except Exception as e:
                messages.error(request, f'Có lỗi khi cập nhật: {e}')
        
        return redirect('users:user_list_page')

    # Nếu là GET, hiển thị trang edit
    return render(request, 'edit_user.html', {'user_obj': user_obj})


@login_required
def delete_user(request, user_id):
    """
    Xử lý xóa người dùng (Delete).
    """
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
        return redirect('users:user_list_page')
        
    if request.method == 'POST':
        user_to_delete = get_object_or_404(User, id=user_id)
        
        # Kiểm tra an toàn: không cho phép xóa chính mình
        if request.user.id == user_to_delete.id:
            messages.error(request, 'Bạn không thể tự xóa chính mình.')
            return redirect('user_list_page')
        
        try:
            username = user_to_delete.username
            user_to_delete.delete()
            messages.success(request, f'Đã xóa người dùng {username}.')
        except Exception as e:
            messages.error(request, f'Có lỗi khi xóa: {e}')
            
    return redirect('user_list_page')