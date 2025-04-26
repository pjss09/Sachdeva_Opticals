import pandas as pd
import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q, Sum, F
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.conf import settings
from twilio.rest import Client

# Local imports
from .forms import (
    CustomerForm, ProductForm, SupplierForm,
    InventoryForm, SalesFilterForm, CustomUserCreationForm,
    PurchaseForm, PrescriptionForm, BillForm
)
from .models import (
    Customer, CustomerHistory, Product,
    Supplier, Inventory, Sale, ProductCategory,
    Purchase, Prescription, Bill
)
from .utils import is_safe_url

User = get_user_model()

# ======================
# Authentication Views
# ======================
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! Please log in.')
        return response

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    next_url = request.GET.get('next')
    if next_url and is_safe_url(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('login')

# ======================
# Dashboard Views
# ======================
@login_required
def dashboard(request):
    # Calculate basic stats for dashboard
    customer_count = Customer.objects.filter(user=request.user).count()
    recent_sales = Sale.objects.filter(created_by=request.user).order_by('-date')[:5]
    low_stock = Inventory.objects.filter(
        quantity__lt=F('product__reorder_level'),
        is_active=True
    )[:5]

    context = {
        'customer_count': customer_count,
        'recent_sales': recent_sales,
        'low_stock': low_stock
    }
    return render(request, "dashboard.html", context)

# ======================
# Customer Management
# ======================
@login_required
def customer_list(request):
    query = request.GET.get('q', '')
    customers = Customer.objects.filter(user=request.user).order_by('-created_at')

    if query:
        customers = customers.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'customers': customers,
        'query': query,
        'total_customers': customers.count()
    }
    return render(request, 'customers/customer_list.html', context)

@login_required
def customer_details(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id, user=request.user)
    purchases = Purchase.objects.filter(customer=customer).select_related('product_type')
    prescriptions = Prescription.objects.filter(customer=customer)
    bills = Bill.objects.filter(customer=customer).prefetch_related('products')

    context = {
        'customer': customer,
        'history': customer.history.all().order_by('-date'),
        'purchases': purchases,
        'prescriptions': prescriptions,
        'bills': bills
    }
    return render(request, 'customers/customer_details.html', context)

@login_required
def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()

            CustomerHistory.objects.create(
                customer=customer,
                description="Customer added.",
                details=f"Customer added by {request.user.username}."
            )

            messages.success(request, 'Customer added successfully!')
            return redirect('customers:customer_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerForm()

    context = {
        'form': form,
        'sph_options': [round(-0.25 * i, 2) for i in range(0, 41)],
        'cyl_options': [round(-0.25 * i, 2) for i in range(0, 41)],
        'axis_options': list(range(0, 181)),
        'add_options': [round(0.75 + 0.25 * i, 2) for i in range(0, 10)],
    }
    return render(request, "customers/add_customer.html", context)

@login_required
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id, user=request.user)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()

            CustomerHistory.objects.create(
                customer=customer,
                description="Customer details updated.",
                details=f"Customer details updated by {request.user.username}."
            )

            messages.success(request, 'Customer updated successfully!')
            return redirect('customers:customer_details', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)

    context = {
        'form': form,
        'customer': customer,
        'sph_options': [round(-0.25 * i, 2) for i in range(0, 41)],
        'cyl_options': [round(-0.25 * i, 2) for i in range(0, 41)],
        'axis_options': list(range(0, 181)),
        'add_options': [round(0.75 + 0.25 * i, 2) for i in range(0, 10)],
    }
    return render(request, "customers/edit_customer.html", context)

@login_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id, user=request.user)
    
    if request.method == "POST":
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customers:customer_list')
    
    return render(request, 'customers/confirm_delete.html', {
        'object': customer,
        'object_type': 'customer'
    })

# ======================
# Purchase & Prescription Views
# ======================
@login_required
def add_purchase_and_prescription(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id, user=request.user)
    
    if request.method == 'POST':
        purchase_form = PurchaseForm(request.POST)
        prescription_form = PrescriptionForm(request.POST)
        
        if purchase_form.is_valid() and prescription_form.is_valid():
            purchase = purchase_form.save(commit=False)
            purchase.customer = customer
            purchase.save()
            
            prescription = prescription_form.save(commit=False)
            prescription.customer = customer
            prescription.purchase = purchase
            prescription.save()
            
            messages.success(request, 'Purchase and prescription added successfully!')
            return redirect('customers:customer_details', customer_id=customer.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        purchase_form = PurchaseForm()
        prescription_form = PrescriptionForm()

    context = {
        'customer': customer,
        'purchase_form': purchase_form,
        'prescription_form': prescription_form,
    }
    return render(request, 'customers/add_transaction.html', context)

@login_required
def view_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    if purchase.customer.user != request.user:
        raise PermissionDenied
    
    try:
        prescription = Prescription.objects.get(purchase=purchase)
    except Prescription.DoesNotExist:
        prescription = None

    context = {
        'purchase': purchase,
        'prescription': prescription,
        'customer': purchase.customer,
    }
    return render(request, 'customers/view_purchase.html', context)

@login_required
def delete_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    if purchase.customer.user != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        customer_id = purchase.customer.id
        purchase.delete()
        messages.success(request, 'Purchase deleted successfully!')
        return redirect('customers:customer_details', customer_id=customer_id)
    
    return render(request, 'customers/confirm_delete.html', {
        'object': purchase,
        'object_type': 'purchase'
    })

@login_required
def delete_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    if prescription.customer.user != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        customer_id = prescription.customer.id
        prescription.delete()
        messages.success(request, 'Prescription deleted successfully!')
        return redirect('customers:customer_details', customer_id=customer_id)
    
    return render(request, 'customers/confirm_delete.html', {
        'object': prescription,
        'object_type': 'prescription'
    })

# ======================
# Bill Management
# ======================
@login_required
def create_bill(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id, user=request.user)
    
    if request.method == 'POST':
        form = BillForm(request.user, request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.customer = customer
            bill.created_by = request.user
            bill.total_amount = sum(product.price for product in form.cleaned_data['products'])
            bill.save()
            form.save_m2m()
            
            messages.success(request, 'Bill created successfully!')
            return redirect('customers:customer_details', customer_id=customer.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BillForm(user=request.user)
    
    context = {
        'customer': customer,
        'form': form,
    }
    return render(request, 'customers/create_bill.html', context)

@login_required
def view_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    if bill.customer.user != request.user:
        raise PermissionDenied
    
    context = {
        'bill': bill,
        'customer': bill.customer,
        'products': bill.products.all()
    }
    return render(request, 'customers/view_bill.html', context)

# ======================
# Inventory Management
# ======================
@login_required
def manage_inventory(request):
    inventory = Inventory.objects.filter(is_active=True).select_related('product', 'supplier')
    total_value = sum(item.total_value() for item in inventory)
    
    context = {
        'inventory': inventory,
        'total_value': total_value
    }
    return render(request, 'inventory/manage_inventory.html', context)

@login_required
def inventory_form(request, inventory_id=None):
    inventory = get_object_or_404(Inventory, id=inventory_id) if inventory_id else None
    form = InventoryForm(request.POST or None, instance=inventory)

    if form.is_valid():
        inventory = form.save(commit=False)
        inventory.created_by = request.user
        inventory.save()
        action = 'updated' if inventory_id else 'created'
        messages.success(request, f'Inventory {action} successfully!')
        return redirect('manage_inventory')

    return render(request, 'inventory/form.html', {'form': form})

@login_required
def toggle_inventory(request, inventory_id):
    inventory = get_object_or_404(Inventory, id=inventory_id)
    inventory.is_active = not inventory.is_active
    inventory.save()
    action = 'activated' if inventory.is_active else 'deactivated'
    messages.success(request, f'Inventory {action} successfully!')
    return redirect('manage_inventory')

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('manage_inventory')
    else:
        form = ProductForm()
    
    return render(request, 'inventory/add_product.html', {'form': form})

@login_required
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.created_by = request.user
            supplier.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('manage_inventory')
    else:
        form = SupplierForm()
    
    return render(request, 'inventory/add_supplier.html', {'form': form})

@login_required
def batch_details(request, batch_number):
    batch_items = Inventory.objects.filter(batch_number=batch_number)
    if not batch_items.exists():
        raise Http404("Batch not found")
    
    context = {
        'batch_items': batch_items,
        'batch_number': batch_number
    }
    return render(request, 'inventory/batch_details.html', context)

# ======================
# Sales & Reporting
# ======================
@login_required
def sales_report(request):
    sales = Sale.objects.filter(created_by=request.user).select_related('product__category')
    form = SalesFilterForm(request.GET or None)

    if form.is_valid():
        sales = form.filter_queryset(sales)

    total_sales = sales.aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'sales': sales,
        'form': form,
        'total_sales': total_sales
    }
    return render(request, 'reports/sales_report.html', context)

@login_required
def export_sales_report(request):
    sales = Sale.objects.filter(created_by=request.user)
    
    # Create a DataFrame from the sales data
    data = []
    for sale in sales:
        data.append({
            'Date': sale.date.strftime('%Y-%m-%d'),
            'Product': sale.product.name,
            'Quantity': sale.quantity,
            'Price': sale.price,
            'Total': sale.total,
            'Customer': sale.customer.get_full_name() if sale.customer else 'N/A'
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel response
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
    
    with pd.ExcelWriter(response) as writer:
        df.to_excel(writer, sheet_name='Sales Report', index=False)
    
    return response

@login_required
def gst_reports(request):
    # Calculate GST reports
    sales = Sale.objects.filter(created_by=request.user)
    gst_data = sales.values('product__category__gst_rate').annotate(
        total_sales=Sum('total'),
        total_tax=Sum(F('total') * F('product__category__gst_rate') / 100)
    ).order_by('product__category__gst_rate')
    
    context = {
        'gst_data': gst_data,
        'total_sales': sum(item['total_sales'] for item in gst_data),
        'total_tax': sum(item['total_tax'] for item in gst_data)
    }
    return render(request, 'reports/gst_reports.html', context)

@login_required
def supplier_ledger(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    inventory_items = Inventory.objects.filter(supplier=supplier).order_by('-date_added')
    
    context = {
        'supplier': supplier,
        'inventory_items': inventory_items,
        'total_value': sum(item.total_value() for item in inventory_items)
    }
    return render(request, 'reports/supplier_ledger.html', context)

# ======================
# Marketing
# ======================
@login_required
def send_promotional_message(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        customers = Customer.objects.filter(user=request.user)
        
        # For SMS (Twilio example)
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            for customer in customers:
                if customer.phone:
                    try:
                        client.messages.create(
                            body=message,
                            from_=settings.TWILIO_PHONE_NUMBER,
                            to=customer.phone
                        )
                    except Exception as e:
                        messages.error(request, f"Failed to send SMS to {customer.get_full_name()}: {str(e)}")
        
        # For Email
        for customer in customers:
            if customer.email:
                try:
                    send_mail(
                        'Promotional Message',
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [customer.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    messages.error(request, f"Failed to send email to {customer.get_full_name()}: {str(e)}")
        
        messages.success(request, 'Promotional messages sent successfully!')
        return redirect('dashboard')
    
    return render(request, 'marketing/send_promotional_message.html')

# ======================
# Alerts
# ======================
@login_required
def inventory_alert(request):
    low_stock = Inventory.objects.filter(
        quantity__lt=F('product__reorder_level'),
        is_active=True
    ).select_related('product', 'supplier')
    
    context = {
        'low_stock_items': low_stock
    }
    return render(request, 'alerts/inventory_alerts.html', context)

# ======================
# Error Handlers
# ======================
def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)