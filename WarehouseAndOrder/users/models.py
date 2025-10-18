# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Chúng ta không cần thêm trường nào ở đây cả.
    # AbstractUser đã có đủ mọi thứ chúng ta cần.
    pass

    def __str__(self):

        return self.username