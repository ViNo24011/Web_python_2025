"""from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, CustomerViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]"""

from django.urls import path
from . import views

app_name = 'partners'

urlpatterns = [
    # URL cho các trang HTML
    path('customers/', views.customer_page, name='customer_page'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:customer_id>/edit/', views.edit_customer, name='edit_customer'),
    path('customers/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),

    # URL cho các trang HTML của nhà cung cấp
    path('suppliers/', views.supplier_page, name='supplier_page'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/<int:supplier_id>/edit/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/<int:supplier_id>/delete/', views.delete_supplier, name='delete_supplier'),
]