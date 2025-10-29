from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inventory'



urlpatterns = [
    # === Các đường dẫn quản lý sản phẩm ===
    path('products/select-warehouse/', views.select_warehouse, name='select_warehouse'),
    path('products/warehouse/<int:warehouse_id>/', views.product_list_by_warehouse, name='product_list_by_warehouse'),
    path('products/warehouse/<int:warehouse_id>/add/', views.add_product_to_warehouse, name='add_product_to_warehouse'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),

    # === Các đường dẫn quản lý kho hàng ===
    path('warehouses/', views.warehouse_page, name='warehouse_page'),
    path('warehouses/add/', views.add_warehouse, name='add_warehouse'), # Xử lý POST từ modal
    path('warehouses/<int:warehouse_id>/edit/', views.edit_warehouse, name='edit_warehouse'), # Trang sửa kho riêng
    path('warehouses/<int:warehouse_id>/delete/', views.delete_warehouse, name='delete_warehouse'), # Xử lý POST xóa kho
]