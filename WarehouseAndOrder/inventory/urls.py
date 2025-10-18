from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inventory'

# Tạo router cho API
router = DefaultRouter()
router.register(r'products', views.ProductViewSet)

urlpatterns = [
     # URL cho trang sản phẩm
    path('products/', views.product_page, name='product_page'),
    # URL để xử lý việc thêm sản phẩm mới
    path('products/add/', views.add_product, name='add_product'),
    # URL để xử lý việc xóa sản phẩm
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    # URL để xử lý việc chỉnh sửa sản phẩm
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    
    # URL cho API, chúng ta đặt nó dưới tiền tố /api/
    path('api/', include(router.urls)),
]