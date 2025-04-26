from django.contrib import admin
from .models import (
    Customer, Purchase, Prescription,
    CustomerHistory, ProductCategory,
    Supplier, Product, Inventory, Sale
)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'gstin', 'contact_person')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'batch_number', 'quantity')

from .models import Bill

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total', 'payment_method')

admin.site.register(Purchase)
admin.site.register(Prescription)
admin.site.register(CustomerHistory)
admin.site.register(ProductCategory)
admin.site.register(Sale)