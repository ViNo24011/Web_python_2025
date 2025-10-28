# reports/views.py

from django.shortcuts import render, get_object_or_404, redirect # Thêm redirect nếu cần sau này
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth # Hàm cắt ngày thành tháng
from django.utils import timezone
from django.http import Http404, JsonResponse # Thêm JsonResponse nếu cần API sau này

# Import models từ các app khác
from transactions.models import ImportReceipt, ExportReceipt
from inventory.models import Warehouse # Import Warehouse
# Import Product và Customer nếu cần cho các báo cáo khác sau này
# from inventory.models import Product
# from partners.models import Customer

from decimal import Decimal
import datetime

# ============= REVENUE REPORT VIEWS =============

# @login_required # Bỏ comment nếu muốn yêu cầu đăng nhập
def revenue_page(request):
    """
    Hiển thị trang tóm tắt doanh thu hàng tháng.
    Nhóm các phiếu nhập và xuất theo tháng, tính tổng và lợi nhuận.
    """

    # --- Tổng hợp dữ liệu Nhập hàng theo Tháng ---
    # Sử dụng annotate -> values -> annotate để nhóm và tính toán
    imports_monthly = ImportReceipt.objects.annotate(
            month=TruncMonth('import_date') # Tạo trường 'month' từ 'import_date'
        ).values(
            'month' # Nhóm theo trường 'month' vừa tạo
        ).annotate(
            import_count=Count('import_id'),       # Đếm số phiếu nhập
            total_import=Sum('total_import_order') # Tính tổng tiền nhập
        ).order_by(
            '-month' # Sắp xếp giảm dần theo tháng
        )

    # --- Tổng hợp dữ liệu Xuất hàng theo Tháng ---
    # Chỉ tính các phiếu đã xác nhận (is_confirmed=True)
    exports_monthly = ExportReceipt.objects.filter(
            is_confirmed=True
        ).annotate(
            month=TruncMonth('export_date')
        ).values(
            'month'
        ).annotate(
            export_count=Count('export_id'),
            total_export=Sum('total_export_order')
        ).order_by(
            '-month'
        )

    # --- Kết hợp dữ liệu Nhập và Xuất ---
    revenue_data = {} # Dùng dictionary để dễ dàng gộp dữ liệu theo tháng

    # Duyệt qua kết quả nhập hàng
    for item in imports_monthly:
        month = item['month']
        revenue_data[month] = {
            'month': month,
            'import_count': item['import_count'],
            'total_import': item['total_import'] or Decimal(0), # Đảm bảo là Decimal, nếu Sum trả về None thì là 0
            'export_count': 0, # Khởi tạo giá trị xuất
            'total_export': Decimal(0),
            'profit': Decimal(0)
        }

    # Duyệt qua kết quả xuất hàng và cập nhật/thêm vào dictionary
    for item in exports_monthly:
        month = item['month']
        if month in revenue_data: # Nếu tháng đã tồn tại (có nhập hàng)
            revenue_data[month]['export_count'] = item['export_count']
            revenue_data[month]['total_export'] = item['total_export'] or Decimal(0)
        else: # Nếu tháng chưa tồn tại (chỉ có xuất hàng)
             revenue_data[month] = {
                'month': month,
                'import_count': 0, # Không có nhập
                'total_import': Decimal(0),
                'export_count': item['export_count'],
                'total_export': item['total_export'] or Decimal(0),
                'profit': Decimal(0)
            }
        # Tính lợi nhuận (cho cả 2 trường hợp trên)
        revenue_data[month]['profit'] = revenue_data[month]['total_export'] - revenue_data[month]['total_import']

    # Chuyển dictionary thành list để dễ duyệt trong template
    monthly_summary = list(revenue_data.values())

    # Tạo context để truyền dữ liệu sang template
    context = {
        'monthly_summary': monthly_summary,
    }
    # Render template 'revenue.html' với context
    return render(request, 'revenue.html', context)


# @login_required # Bỏ comment nếu muốn yêu cầu đăng nhập
@login_required
def revenue_detail_page(request, year, month):
    """
    Hiển thị chi tiết doanh thu theo từng kho cho một tháng và năm cụ thể.
    Tính toán tổng tiền nhập/xuất, lợi nhuận và số lượng đơn nhập/xuất.
    """
    try:
        # Kiểm tra tính hợp lệ của năm, tháng và tạo đối tượng date
        target_date = datetime.date(year, month, 1)
    except ValueError:
        raise Http404("Ngày không hợp lệ.")

    # --- Lấy tất cả các kho hàng ---
    warehouses = Warehouse.objects.all()
    # Tạo dictionary để lưu trữ kết quả cho từng kho, key là ID kho
    warehouse_details = {
        wh.id: {
            'id': wh.id, # Keep id for internal use if needed
            'name': wh.name,
            # 'location': wh.location, # No longer needed for display
            'import_count': 0, # --- THÊM: Khởi tạo số đơn nhập ---
            'total_import': Decimal(0),
            'export_count': 0, # --- THÊM: Khởi tạo số đơn xuất ---
            'total_export': Decimal(0),
            'profit': Decimal(0)
        } for wh in warehouses
    }

    # --- Tổng hợp Nhập hàng trong tháng, nhóm theo kho ---
    imports_in_month_by_wh = ImportReceipt.objects.filter(
            import_date__year=year, import_date__month=month
        ).values(
            'warehouse' # Nhóm theo warehouse_id
        ).annotate(
            total_import=Sum('total_import_order'), # Tính tổng tiền nhập
            import_count=Count('import_id')         # --- THÊM: Đếm số đơn nhập ---
        )

    # Cập nhật kết quả vào dictionary warehouse_details
    for item in imports_in_month_by_wh:
        wh_id = item['warehouse']
        if wh_id in warehouse_details:
            warehouse_details[wh_id]['total_import'] = item['total_import'] or Decimal(0)
            warehouse_details[wh_id]['import_count'] = item['import_count'] # --- THÊM: Lưu số đơn nhập ---

    # --- Tổng hợp Xuất hàng (đã xác nhận) trong tháng, nhóm theo kho ---
    exports_in_month_by_wh = ExportReceipt.objects.filter(
            is_confirmed=True, export_date__year=year, export_date__month=month
        ).values(
            'warehouse' # Nhóm theo warehouse_id
        ).annotate(
            total_export=Sum('total_export_order'), # Tính tổng tiền xuất
            export_count=Count('export_id')         # --- THÊM: Đếm số đơn xuất ---
        )

    # Cập nhật kết quả vào dictionary warehouse_details
    for item in exports_in_month_by_wh:
        wh_id = item['warehouse']
        if wh_id in warehouse_details:
            warehouse_details[wh_id]['total_export'] = item['total_export'] or Decimal(0)
            warehouse_details[wh_id]['export_count'] = item['export_count'] # --- THÊM: Lưu số đơn xuất ---

    # --- Tính lợi nhuận cho từng kho và chuyển thành list ---
    warehouse_summary_list = []
    for wh_id, details in warehouse_details.items():
        details['profit'] = details['total_export'] - details['total_import'] # Tính lợi nhuận
        warehouse_summary_list.append(details) # Thêm vào list kết quả

    # Sắp xếp list theo tên kho (tùy chọn)
    warehouse_summary_list.sort(key=lambda x: x.get('name', ''))

    # Tạo context để truyền dữ liệu sang template
    context = {
        'year': year,
        'month': month,
        'target_date': target_date,
        'warehouse_summary': warehouse_summary_list,
    }
    # Render template 'detail.html' với context
    return render(request, 'detail.html', context)


    # @login_required # Bỏ comment nếu muốn yêu cầu đăng nhập
def warehouse_imports_detail(request, year, month, warehouse_id):
    """
    Hiển thị danh sách phiếu nhập của một kho cụ thể trong tháng.
    """
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    try:
        target_date = datetime.date(year, month, 1)
    except ValueError:
        raise Http404("Ngày không hợp lệ.")

    # Lấy danh sách phiếu nhập theo kho, năm, tháng
    import_receipts = ImportReceipt.objects.filter(
        warehouse=warehouse,
        import_date__year=year,
        import_date__month=month
    ).select_related('supplier').order_by('-import_date') # Sắp xếp mới nhất trước

    context = {
        'warehouse': warehouse,
        'target_date': target_date,
        'import_receipts': import_receipts,
        'year': year, # Truyền lại để dùng trong nút quay lại nếu cần
        'month': month,
    }
    return render(request, 'warehouse_imports_detail.html', context)


# @login_required # Bỏ comment nếu muốn yêu cầu đăng nhập
def warehouse_exports_detail(request, year, month, warehouse_id):
    """
    Hiển thị danh sách phiếu xuất (đã xác nhận) của một kho cụ thể trong tháng.
    """
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)
    try:
        target_date = datetime.date(year, month, 1)
    except ValueError:
        raise Http404("Ngày không hợp lệ.")

    # Lấy danh sách phiếu xuất (đã xác nhận) theo kho, năm, tháng
    export_receipts = ExportReceipt.objects.filter(
        warehouse=warehouse,
        is_confirmed=True, # Thường chỉ quan tâm phiếu đã xác nhận
        export_date__year=year,
        export_date__month=month
    ).order_by('-export_date') # Sắp xếp mới nhất trước

    context = {
        'warehouse': warehouse,
        'target_date': target_date,
        'export_receipts': export_receipts,
        'year': year, # Truyền lại để dùng trong nút quay lại nếu cần
        'month': month,
    }
    return render(request, 'warehouse_exports_detail.html', context)