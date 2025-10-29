from django.apps import AppConfig # lớp gốc mà Django dùng để định nghĩa cấu hình của một app.


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
