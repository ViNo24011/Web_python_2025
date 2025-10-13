from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    min_quantity = models.IntegerField(default=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return self.name