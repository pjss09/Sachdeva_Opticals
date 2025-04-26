from django.urls import path, include
from django.contrib import admin
from . import views

app_name = 'customers'

urlpatterns = [
    # Authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    
    # Customer Management
    path('', views.customer_list, name='customer_list'),
    path('customers/view/', views.customer_list, name='view_customers'),  # Added this line
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:customer_id>/', views.customer_details, name='customer_details'),
    path('customers/edit/<int:customer_id>/', views.edit_customer, name='edit_customer'),
    path('customers/delete/<int:customer_id>/', views.delete_customer, name='delete_customer'),
    path('customers/<int:customer_id>/transaction/', views.add_purchase_and_prescription, name='add_purchase_and_prescription'),
    
    # Purchase/Prescription Management
    path('purchases/<int:purchase_id>/', views.view_purchase, name='view_purchase'),
    path('purchases/delete/<int:purchase_id>/', views.delete_purchase, name='delete_purchase'),
    path('prescriptions/delete/<int:prescription_id>/', views.delete_prescription, name='delete_prescription'),
    
    # Inventory Management
    path('inventory/', views.manage_inventory, name='manage_inventory'),
    path('inventory/add/', views.inventory_form, name='add_inventory'),
    path('inventory/edit/<int:inventory_id>/', views.inventory_form, name='edit_inventory'),
    path('inventory/add-product/', views.add_product, name='add_product'),
    path('inventory/add-supplier/', views.add_supplier, name='add_supplier'),
    path('batch/<str:batch_number>/', views.batch_details, name='batch_details'),
    
    # Sales & Billing
    path('sales/', views.sales_report, name='sales_report'),
    path('sales/export/', views.export_sales_report, name='export_sales_report'),
    path('billing/create/', views.create_bill, name='create_bill'),
    
    # Reports
    path('reports/gst/', views.gst_reports, name='gst_reports'),
    path('supplier/<int:supplier_id>/ledger/', views.supplier_ledger, name='supplier_ledger'),
    
    # Marketing
    path('send-promotional-message/', views.send_promotional_message, name='send_promotional_message'),
    
    # Alerts
    path('alerts/', views.inventory_alert, name='inventory_alerts'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin
    path('django-admin/', admin.site.urls),
    
]