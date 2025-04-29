from django.contrib import admin
#accessing our models 
from .models import *
# Register your models here.
admin.site.register(Procurement)
admin.site.register(Stock)
admin.site.register(Produce)
admin.site.register(Dealer)
admin.site.register(Branch)
admin.site.register(CreditSale)
admin.site.register(Sale)
