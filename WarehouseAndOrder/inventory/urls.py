from django.urls import path, include
from rest_framework.routers import DefaultRouter # Bỏ comment nếu dùng API
from . import views

app_name = 'inventory'



urlpatterns = [
    # --- URLS MỚI CHO LUỒNG XEM SẢN PHẨM ---
    path('products/select-warehouse/', views.select_warehouse, name='select_warehouse'),

    # 2. Trang danh sách sản phẩm theo kho (sẽ dùng file product.html)
    path('products/warehouse/<int:warehouse_id>/', views.product_list_by_warehouse, name='product_list_by_warehouse'),

    # 3. URL xử lý THÊM sản phẩm VÀO KHO CỤ THỂ (gọi từ modal trong product.html)
    path('products/warehouse/<int:warehouse_id>/add/', views.add_product_to_warehouse, name='add_product_to_warehouse'),

    # --- URLS CŨ (giữ lại cho sửa/xóa) ---
    # Sửa sản phẩm (sẽ dùng file edit_product.html)
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    # Xóa sản phẩm (xử lý trong views.py)
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),

    # --- URLS CHO KHO HÀNG (giữ nguyên) ---
    path('warehouses/', views.warehouse_page, name='warehouse_page'),
    path('warehouses/add/', views.add_warehouse, name='add_warehouse'), # Xử lý POST từ modal
    path('warehouses/<int:warehouse_id>/edit/', views.edit_warehouse, name='edit_warehouse'), # Trang sửa kho riêng
    path('warehouses/<int:warehouse_id>/delete/', views.delete_warehouse, name='delete_warehouse'), # Xử lý POST xóa kho
]