from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from food import models


admin.site.register(models.CustomUser)
admin.site.register(models.Notification)
admin.site.register(models.OrderItems)
admin.site.register(models.Basket)
