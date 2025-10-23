from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'transactions'

# Router cho API
router = DefaultRouter()
router.register(r'import-receipts', views.ImportReceiptViewSet)
router.register(r'export-receipts', views.ExportReceiptViewSet)

urlpatterns = [
    # ============= IMPORT URLS =============
    # Trang danh sách phiếu nhập
    path('import-receipts/', views.import_receipt_page, name='import_receipt_page'),
    # Trang tạo phiếu nhập mới
    path('import-receipts/create/', views.create_import_receipt_page, name='create_import_receipt_page'),
    # Xử lý thêm phiếu nhập
    path('import-receipts/add/', views.add_import_receipt, name='add_import_receipt'),
    # Trang chỉnh sửa phiếu nhập
    path('import-receipts/<int:import_id>/edit/', views.edit_import_receipt_page, name='edit_import_receipt_page'),
    # Xử lý cập nhật phiếu nhập
    path('import-receipts/<int:import_id>/update/', views.update_import_receipt, name='update_import_receipt'),
    # Xóa phiếu nhập
    path('import-receipts/<int:import_id>/delete/', views.delete_import_receipt, name='delete_import_receipt'),
    # Xác nhận phiếu nhập
    path('import-receipts/<int:import_id>/confirm/', views.confirm_import_receipt, name='confirm_import_receipt'),
    
    # ============= EXPORT URLS =============
    # Trang danh sách phiếu xuất
    path('export-receipts/', views.export_receipt_page, name='export_receipt_page'),
    # Trang tạo phiếu xuất mới
    path('export-receipts/create/', views.create_export_receipt_page, name='create_export_receipt_page'),
    # Xử lý thêm phiếu xuất
    path('export-receipts/add/', views.add_export_receipt, name='add_export_receipt'),
    # Trang chỉnh sửa phiếu xuất
    path('export-receipts/<int:export_id>/edit/', views.edit_export_receipt_page, name='edit_export_receipt_page'),
    # Xử lý cập nhật phiếu xuất
    path('export-receipts/<int:export_id>/update/', views.update_export_receipt, name='update_export_receipt'),
    # Xóa phiếu xuất
    path('export-receipts/<int:export_id>/delete/', views.delete_export_receipt, name='delete_export_receipt'),
    # Xác nhận phiếu xuất
    path('export-receipts/<int:export_id>/confirm/', views.confirm_export_receipt, name='confirm_export_receipt'),
    # Đánh dấu đã giao hàng
    path('export-receipts/<int:export_id>/delivered/', views.mark_as_delivered, name='mark_as_delivered'),
    
    # ============= AJAX API =============
    # Lấy thông tin sản phẩm
    path('api/get-product-info/', views.get_product_info, name='get_product_info'),
    
    # ============= REST API =============
    path('api/', include(router.urls)),
]