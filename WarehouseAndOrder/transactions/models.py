from django.db import models
from django.utils import timezone
from inventory.models import Product
from partners.models import Supplier, Customer

# --- IMPORT RECEIPT MODEL ---
class ImportReceipt(models.Model):
    import_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='import_receipts'
    )
    import_date = models.DateTimeField(default=timezone.now)
    total_import_order = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0
    )
    note = models.TextField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-import_date']

    def __str__(self):
        supplier_name = self.supplier.supplier_name if self.supplier else "N/A"
        return f"Import #{self.import_id} - {supplier_name}"

    def calculate_total(self):
        """Tính tổng tiền của phiếu nhập"""
        total = sum(
            detail.quantity * detail.price 
            for detail in self.import_details.all()
        )
        self.total_import_order = total
        self.save()
        return total


# --- IMPORT DETAIL MODEL ---
class ImportDetail(models.Model):
    import_receipt = models.ForeignKey(
        ImportReceipt, 
        on_delete=models.CASCADE,
        related_name='import_details'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='import_details'
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.name} (Import #{self.import_receipt.import_id})"

    def get_subtotal(self):
        """Tính thành tiền của sản phẩm"""
        return self.quantity * self.price


# --- EXPORT RECEIPT MODEL ---
class ExportReceipt(models.Model):
    DELIVERY_STATUS_CHOICES = (
        ('pending', 'Chờ xác nhận'),
        ('shipping', 'Đang vận chuyển'),
        ('delivered', 'Đã giao'),
    )

    export_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True, null=True)
    customer_address = models.CharField(max_length=255)
    export_date = models.DateTimeField(default=timezone.now)
    total_export_order = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0
    )
    note = models.TextField(blank=True, null=True)
    delivery_status = models.CharField(
        max_length=20, 
        choices=DELIVERY_STATUS_CHOICES, 
        default='pending'
    )
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-export_date']

    def __str__(self):
        return f"Export #{self.export_id} - {self.customer_name}"

    def calculate_total(self):
        """Tính tổng tiền của phiếu xuất"""
        total = sum(
            detail.quantity * detail.price 
            for detail in self.export_details.all()
        )
        self.total_export_order = total
        self.save()
        return total

    def get_delivery_status_display_custom(self):
        """Hiển thị trạng thái giao hàng"""
        status_map = {
            'pending': 'Chờ xác nhận',
            'shipping': 'Đang vận chuyển',
            'delivered': 'Đã giao'
        }
        return status_map.get(self.delivery_status, self.delivery_status)


# --- EXPORT DETAIL MODEL ---
class ExportDetail(models.Model):
    export_receipt = models.ForeignKey(
        ExportReceipt, 
        on_delete=models.CASCADE,
        related_name='export_details'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='export_details'
    )
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} (Export #{self.export_receipt.export_id})"

    def get_subtotal(self):
        """Tính thành tiền của sản phẩm"""
        return self.quantity * self.price