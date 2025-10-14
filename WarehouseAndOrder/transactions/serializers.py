from rest_framework import serializers
from .models import ImportReceipt, ImportDetail, ExportReceipt, ExportDetail

class ImportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportDetail
        fields = '__all__'

class ImportReceiptSerializer(serializers.ModelSerializer):
    details = ImportDetailSerializer(many=True, read_only=True, source='importdetail_set')

    class Meta:
        model = ImportReceipt
        fields = '__all__'

class ExportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportDetail
        fields = '__all__'

class ExportReceiptSerializer(serializers.ModelSerializer):
    details = ExportDetailSerializer(many=True, read_only=True, source='exportdetail_set')

    class Meta:
        model = ExportReceipt
        fields = '__all__'
