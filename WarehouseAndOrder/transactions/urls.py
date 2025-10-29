from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'transactions'

# Router cho API
router = DefaultRouter()
router.register(r'import-receipts', views.ImportReceiptViewSet)
router.register(r'export-receipts', views.ExportReceiptViewSet)

urlpatterns = [
    # Trang danh sách phiếu nhập
    path('import-receipts/', views.import_receipt_page, name='import_receipt_page'),
    path('import-receipts/create/', views.create_import_receipt_page, name='create_import_receipt_page'),
    path('import-receipts/add/', views.add_import_receipt, name='add_import_receipt'),
    path('import-receipts/<int:import_id>/edit/', views.edit_import_receipt_page, name='edit_import_receipt_page'),
    path('import-receipts/<int:import_id>/update/', views.update_import_receipt, name='update_import_receipt'),
    path('import-receipts/<int:import_id>/delete/', views.delete_import_receipt, name='delete_import_receipt'),
    path('import-receipts/<int:import_id>/confirm/', views.confirm_import_receipt, name='confirm_import_receipt'),

    # Trang danh sách phiếu xuất
    path('export-receipts/', views.export_receipt_page, name='export_receipt_page'),
    path('export-receipts/create/', views.create_export_receipt_page, name='create_export_receipt_page'),
    path('export-receipts/add/', views.add_export_receipt, name='add_export_receipt'),
    path('export-receipts/<int:export_id>/edit/', views.edit_export_receipt_page, name='edit_export_receipt_page'),
    path('export-receipts/<int:export_id>/update/', views.update_export_receipt, name='update_export_receipt'),
    path('export-receipts/<int:export_id>/delete/', views.delete_export_receipt, name='delete_export_receipt'),
    path('export-receipts/<int:export_id>/confirm/', views.confirm_export_receipt, name='confirm_export_receipt'),
    path('export-receipts/<int:export_id>/delivered/', views.mark_as_delivered, name='mark_as_delivered'),
    path('api/get-product-info/', views.get_product_info, name='get_product_info'),
    
    # API routes
    path('api/', include(router.urls)),
]