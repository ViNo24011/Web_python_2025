from rest_framework import serializers
from .models import ImportReceipt, ImportDetail, ExportReceipt, ExportDetail
from inventory.models import Product

# ============= IMPORT SERIALIZERS =============
class ImportDetailSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = ImportDetail
        fields = ['id', 'product', 'name', 'price', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        """Tính thành tiền"""
        return obj.quantity * obj.price


class ImportReceiptSerializer(serializers.ModelSerializer):
    import_details = ImportDetailSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(
        source='supplier.supplier_name', 
        read_only=True
    )
    
    class Meta:
        model = ImportReceipt
        fields = [
            'import_id', 'supplier', 'supplier_name', 'import_date',
            'total_import_order', 'note', 'is_confirmed', 'import_details'
        ]


# ============= EXPORT SERIALIZERS =============
class ExportDetailSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = ExportDetail
        fields = ['id', 'product', 'name', 'price', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        """Tính thành tiền"""
        return obj.quantity * obj.price


class ExportReceiptSerializer(serializers.ModelSerializer):
    export_details = ExportDetailSerializer(many=True, read_only=True)
    delivery_status_display = serializers.CharField(
        source='get_delivery_status_display_custom',
        read_only=True
    )
    
    class Meta:
        model = ExportReceipt
        fields = [
            'export_id', 'customer_name', 'customer_phone', 
            'customer_email', 'customer_address', 'export_date',
            'total_export_order', 'note', 'delivery_status', 
            'delivery_status_display', 'is_confirmed', 'export_details'
        ]