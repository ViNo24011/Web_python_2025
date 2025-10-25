from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from rest_framework import viewsets
from .models import ImportReceipt, ImportDetail, ExportReceipt, ExportDetail
from .serializers import ImportReceiptSerializer, ExportReceiptSerializer
from inventory.models import Product
from partners.models import Supplier, Customer
from decimal import Decimal

# ============= IMPORT API VIEWS =============
class ImportReceiptViewSet(viewsets.ModelViewSet):  
    queryset = ImportReceipt.objects.all().order_by('-import_date')
    serializer_class = ImportReceiptSerializer


# ============= EXPORT API VIEWS =============
class ExportReceiptViewSet(viewsets.ModelViewSet):
    queryset = ExportReceipt.objects.all().order_by('-export_date')
    serializer_class = ExportReceiptSerializer


# ============= IMPORT TEMPLATE VIEWS =============
# @login_required
def import_receipt_page(request):
    """Trang danh sách phiếu nhập"""
    import_receipts = ImportReceipt.objects.all().order_by('-import_date')
    context = {
        'import_receipts': import_receipts
    }
    return render(request, 'import_receipt.html', context)


# @login_required
def create_import_receipt_page(request):
    """Trang tạo phiếu nhập mới"""
    suppliers = Supplier.objects.all()
    products = Product.objects.all()
    context = {
        'suppliers': suppliers,
        'products': products
    }
    return render(request, 'create_import_receipt.html', context)

# @login_required
@transaction.atomic
def add_import_receipt(request):
    """Xử lý thêm phiếu nhập mới"""
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        note = request.POST.get('note', '')
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        
        if not supplier_id:
            return redirect('transactions:create_import_receipt_page')
        
        import_receipt = ImportReceipt.objects.create(
            supplier_id=supplier_id,
            note=note,
            is_confirmed=False
        )
        
        for product_id, quantity in zip(product_ids, quantities):
            if product_id and quantity:
                try:
                    product = Product.objects.get(id=product_id)
                    ImportDetail.objects.create(
                        import_receipt=import_receipt,
                        product=product,
                        name=product.name,
                        price=product.price,
                        quantity=int(quantity)
                    )
                except Product.DoesNotExist:
                    continue
        
        import_receipt.calculate_total()
        return redirect('transactions:import_receipt_page')
    
    return redirect('transactions:create_import_receipt_page')


# @login_required
def edit_import_receipt_page(request, import_id):
    """Trang chỉnh sửa phiếu nhập"""
    import_receipt = get_object_or_404(ImportReceipt, import_id=import_id)
    
    if import_receipt.is_confirmed:
        return redirect('transactions:import_receipt_page')
    
    suppliers = Supplier.objects.all()
    products = Product.objects.all()
    context = {
        'import_receipt': import_receipt,
        'suppliers': suppliers,
        'products': products
    }
    return render(request, 'edit_import_receipt.html', context)


# @login_required
@transaction.atomic
def update_import_receipt(request, import_id):
    """Xử lý cập nhật phiếu nhập"""
    import_receipt = get_object_or_404(ImportReceipt, import_id=import_id)
    
    if import_receipt.is_confirmed:
        return redirect('transactions:import_receipt_page')
    
    if request.method == 'POST':
        import_receipt.supplier_id = request.POST.get('supplier')
        import_receipt.note = request.POST.get('note', '')
        import_receipt.save()
        
        import_receipt.import_details.all().delete()
        
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        
        for product_id, quantity in zip(product_ids, quantities):
            if product_id and quantity:
                try:
                    product = Product.objects.get(id=product_id)
                    ImportDetail.objects.create(
                        import_receipt=import_receipt,
                        product=product,
                        name=product.name,
                        price=product.price,
                        quantity=int(quantity)
                    )
                except Product.DoesNotExist:
                    continue
        
        import_receipt.calculate_total()
        return redirect('transactions:import_receipt_page')
    
    return redirect('transactions:edit_import_receipt_page', import_id=import_id)


# @login_required
@transaction.atomic
def delete_import_receipt(request, import_id):
    """Xóa phiếu nhập"""
    import_receipt = get_object_or_404(ImportReceipt, import_id=import_id)
    
    if import_receipt.is_confirmed:
        return redirect('transactions:import_receipt_page')
    
    if request.method == 'POST':
        import_receipt.delete()
    
    return redirect('transactions:import_receipt_page')


# @login_required
@transaction.atomic
def confirm_import_receipt(request, import_id):
    """Xác nhận phiếu nhập và cập nhật tồn kho"""
    import_receipt = get_object_or_404(ImportReceipt, import_id=import_id)
    
    if import_receipt.is_confirmed:
        return redirect('transactions:import_receipt_page')
    
    if request.method == 'POST':
        for detail in import_receipt.import_details.all():
            product = detail.product
            product.quantity += detail.quantity
            product.save()
        
        import_receipt.is_confirmed = True
        import_receipt.save()
    
    return redirect('transactions:import_receipt_page')


# ============= EXPORT TEMPLATE VIEWS =============
# @login_required
def export_receipt_page(request):
    """Trang danh sách phiếu xuất"""
    export_receipts = ExportReceipt.objects.all().order_by('-export_date')
    context = {
        'export_receipts': export_receipts
    }
    return render(request, 'export_receipt.html', context)


# @login_required
def create_export_receipt_page(request):
    """Trang tạo phiếu xuất mới"""
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'create_export_receipt.html', context)


# @login_required
@transaction.atomic
def add_export_receipt(request):
    """Xử lý thêm phiếu xuất mới"""
    if request.method == 'POST':
        # Lấy thông tin khách hàng
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        customer_email = request.POST.get('customer_email', '')
        customer_address = request.POST.get('customer_address')
        note = request.POST.get('note', '')
        
        # Lấy danh sách sản phẩm
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        
        if not all([customer_name, customer_phone, customer_address]):
            return redirect('transactions:create_export_receipt_page')
        
        # Tạo phiếu xuất
        export_receipt = ExportReceipt.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            customer_address=customer_address,
            note=note,
            is_confirmed=False,
            delivery_status='pending'
        )
        
        # Thêm chi tiết sản phẩm với giá = giá gốc * 150%
        for product_id, quantity in zip(product_ids, quantities):
            if product_id and quantity:
                try:
                    product = Product.objects.get(id=product_id)
                    # Giá bán = giá gốc * 1.5 (150%)
                    selling_price = product.price * Decimal('1.5')
                    
                    ExportDetail.objects.create(
                        export_receipt=export_receipt,
                        product=product,
                        name=product.name,
                        price=selling_price,
                        quantity=int(quantity)
                    )
                except Product.DoesNotExist:
                    continue
        
        # Tính tổng tiền
        export_receipt.calculate_total()
        
        return redirect('transactions:export_receipt_page')
    
    return redirect('transactions:create_export_receipt_page')


# @login_required
def edit_export_receipt_page(request, export_id):
    """Trang chỉnh sửa phiếu xuất"""
    export_receipt = get_object_or_404(ExportReceipt, export_id=export_id)
    
    if export_receipt.is_confirmed:
        return redirect('transactions:export_receipt_page')
    
    products = Product.objects.all()
    context = {
        'export_receipt': export_receipt,
        'products': products
    }
    return render(request, 'edit_export_receipt.html', context)


# @login_required
@transaction.atomic
def update_export_receipt(request, export_id):
    """Xử lý cập nhật phiếu xuất"""
    export_receipt = get_object_or_404(ExportReceipt, export_id=export_id)
    
    if export_receipt.is_confirmed:
        return redirect('transactions:export_receipt_page')
    
    if request.method == 'POST':
        # Cập nhật thông tin khách hàng
        export_receipt.customer_name = request.POST.get('customer_name')
        export_receipt.customer_phone = request.POST.get('customer_phone')
        export_receipt.customer_email = request.POST.get('customer_email', '')
        export_receipt.customer_address = request.POST.get('customer_address')
        export_receipt.note = request.POST.get('note', '')
        export_receipt.save()
        
        # Xóa chi tiết cũ
        export_receipt.export_details.all().delete()
        
        # Thêm chi tiết mới
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        
        for product_id, quantity in zip(product_ids, quantities):
            if product_id and quantity:
                try:
                    product = Product.objects.get(id=product_id)
                    selling_price = product.price * Decimal('1.5')
                    
                    ExportDetail.objects.create(
                        export_receipt=export_receipt,
                        product=product,
                        name=product.name,
                        price=selling_price,
                        quantity=int(quantity)
                    )
                except Product.DoesNotExist:
                    continue
        
        # Tính lại tổng tiền
        export_receipt.calculate_total()
        
        return redirect('transactions:export_receipt_page')
    
    return redirect('transactions:edit_export_receipt_page', export_id=export_id)


# @login_required
@transaction.atomic
def delete_export_receipt(request, export_id):
    """Xóa phiếu xuất"""
    export_receipt = get_object_or_404(ExportReceipt, export_id=export_id)
    
    if export_receipt.is_confirmed:
        return redirect('transactions:export_receipt_page')
    
    if request.method == 'POST':
        export_receipt.delete()
    
    return redirect('transactions:export_receipt_page')


# @login_required
@transaction.atomic
def confirm_export_receipt(request, export_id):
    """Xác nhận phiếu xuất, cập nhật tồn kho và thông tin khách hàng"""
    export_receipt = get_object_or_404(ExportReceipt, export_id=export_id)
    
    if export_receipt.is_confirmed:
        return redirect('transactions:export_receipt_page')
    
    if request.method == 'POST':
        # Kiểm tra tồn kho trước khi xuất
        for detail in export_receipt.export_details.all():
            product = detail.product
            if product.quantity < detail.quantity:
                # Có thể thêm message error ở đây
                return redirect('transactions:export_receipt_page')
        
        # Cập nhật số lượng sản phẩm trong kho
        for detail in export_receipt.export_details.all():
            product = detail.product
            product.quantity -= detail.quantity
            product.save()
        
        # Cập nhật hoặc tạo mới thông tin khách hàng
        customer, created = Customer.objects.update_or_create(
            phone=export_receipt.customer_phone,
            defaults={
                'name': export_receipt.customer_name,
                'email': export_receipt.customer_email,
                'address': export_receipt.customer_address
            }
        )
        
        # Đánh dấu đã xác nhận và chuyển sang đang vận chuyển
        export_receipt.is_confirmed = True
        export_receipt.delivery_status = 'shipping'
        export_receipt.save()
    
    return redirect('transactions:export_receipt_page')


# @login_required
@transaction.atomic
def mark_as_delivered(request, export_id):
    """Đánh dấu phiếu xuất đã giao hàng"""
    export_receipt = get_object_or_404(ExportReceipt, export_id=export_id)
    
    if not export_receipt.is_confirmed:
        return redirect('transactions:export_receipt_page')
    
    if request.method == 'POST':
        export_receipt.delivery_status = 'delivered'
        export_receipt.save()
    
    return redirect('transactions:export_receipt_page')


# ============= AJAX API =============
# @login_required
def get_product_info(request):
    """API lấy thông tin sản phẩm theo ID"""
    product_id = request.GET.get('product_id')
    
    try:
        product = Product.objects.get(id=product_id)
        # Tính giá bán = giá gốc * 1.5
        selling_price = float(product.price) * 1.5
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'selling_price': str(selling_price),
                'unit': product.unit,
                'category_name': product.category_name,
                'current_quantity': product.quantity
            }
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Không tìm thấy sản phẩm'
        })