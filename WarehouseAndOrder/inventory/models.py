from django.db import models

# Create your models here.

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    category_name = models.CharField(max_length=100, default="General")
    quantity = models.IntegerField(default=0)
    min_quantity = models.IntegerField(default=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    
    # --- THÊM KHÓA NGOẠI TẠI ĐÂY ---
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.PROTECT,  
        related_name="products",   
        null=True,             
        blank=True                
    )

    def __str__(self):
        return self.name