
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inventory'

# Tạo router cho API
router = DefaultRouter()
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    # --- Các URL cho Sản phẩm (Product) ---
    path('products/', views.product_page, name='product_page'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),

    # --- CÁC URL MỚI CHO KHO HÀNG (Warehouse) ---
    path('warehouses/', views.warehouse_page, name='warehouse_page'),
    path('warehouses/add/', views.add_warehouse, name='add_warehouse'),
    path('warehouses/<int:warehouse_id>/edit/', views.edit_warehouse, name='edit_warehouse'),
    path('warehouses/<int:warehouse_id>/delete/', views.delete_warehouse, name='delete_warehouse'),
]
