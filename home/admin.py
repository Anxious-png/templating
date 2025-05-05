from django.contrib import admin
#accessing our models 
from .models import *
from django.contrib.auth.admin import UserAdmin
# Register your models here.
admin.site.register(Procurement)
admin.site.register(Stock)
admin.site.register(Produce)
admin.site.register(Dealer)
#admin.site.register(Branch)
admin.site.register(CreditSale)
admin.site.register(Sale)
class CustomUserAdmin(UserAdmin):
    model = Userprofile
    list_display = ['username', 'email', 'is_manager', 'is_salesagent', 'is_owner', 'branch']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_manager', 'is_salesagent', 'is_owner', 'address', 'phonenumber', 'gender', 'branch')}),
    )

admin.site.register(Userprofile, CustomUserAdmin)
