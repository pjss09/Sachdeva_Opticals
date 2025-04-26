from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db.models import JSONField  # For PostgreSQL, or use models.JSONField in Django 3.1+

# Customer Model
class Customer(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    # Personal Information
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    first_name = models.CharField(max_length=100,null=True,blank=True)
    last_name = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15,null=True,blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices,null=True,blank=True)
    prescription_date = models.DateField(null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    # Prescription Details
    sph_left = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sph_right = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cyl_left = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cyl_right = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    axis_left = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(180)]
    )
    axis_right = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(180)]
    )
    add_left = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    add_right = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vision_left = models.CharField(max_length=255, null=True, blank=True)
    vision_right = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        unique_together = ('user', 'phone')
        ordering = ['-prescription_date']

        
# Purchase Model
class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='purchases', null=True, blank=True)
    product_type = models.CharField(max_length=50,null=True,blank=True)  # e.g., spectacles, sunglasses, lenses, etc.
    details = JSONField(default=dict)  # Provide a default value
    date_of_purchase = models.DateField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return f"Purchase for {self.customer.full_name()} on {self.date_of_purchase}"
    
    def total_cost(self):
        # Calculate total cost based on details (e.g., lens_price + frame_price)
        lens_price = self.details.get('lens_price', 0) or 0
        frame_price = self.details.get('frame_price', 0) or 0
        return lens_price + frame_price


# Prescription Model
class Prescription(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='prescriptions')
    sph_left = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sph_right = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cyl_left = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cyl_right = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    axis_left = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(180)])
    axis_right = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(180)])
    add_left = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    add_right = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vision_left = models.CharField(max_length=255, null=True, blank=True)
    vision_right = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return f"Prescription for {self.customer.full_name()} on {self.date}"


# Customer History Model
class CustomerHistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='history')
    date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255)
    details = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.customer.full_name()} - {self.description} on {self.date}"


# Product Category Model
class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Supplier Model
class Supplier(models.Model):
    LENS_TYPES = [
        ('SV', 'Single Vision'),
        ('BF', 'Bifocal'),
        ('PL', 'Progressive'),
    ]
    FRAME_MATERIALS = [
        ('AC', 'Acetate'),
        ('MT', 'Metal'),
        ('TI', 'Titanium'),
    ]

    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    gstin = models.CharField(max_length=15, validators=[RegexValidator(regex=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', message="Enter a valid GSTIN (e.g., 12ABCDE1234F1Z5).")], null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)

    def __str__(self):
        return self.name


# Product Model
class Product(models.Model):
    LENS_TYPES = [
        ('SV', 'Single Vision'),
        ('BF', 'Bifocal'),
        ('PL', 'Progressive'),
    ]
    FRAME_MATERIALS = [
        ('AC', 'Acetate'),
        ('MT', 'Metal'),
        ('TI', 'Titanium'),
    ]

    name = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    model_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18.0)
    reorder_level = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hsn_code = models.CharField(max_length=10, blank=True, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lens_type = models.CharField(max_length=2, choices=LENS_TYPES, blank=True, null=True)
    frame_material = models.CharField(max_length=2, choices=FRAME_MATERIALS, blank=True, null=True)
    base_curve = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    diameter = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.brand})"

    def total_cost(self):
        return self.price * (1 + (self.gst_percentage / 100))


# Inventory Model
class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    batch_number = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    mfg_date = models.DateField(null=True, blank=True)
    import_duty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - Batch: {self.batch_number}"

    def total_cost(self):
        return self.quantity * self.purchase_price

    def total_value(self):
        return self.quantity * self.selling_price


# Sale Model
class Sale(models.Model):
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT,null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units on {self.date}"


# Bill Model
class Bill(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product)
    date = models.DateTimeField(auto_now_add=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=4, choices=PAYMENT_METHODS)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"Bill #{self.id} - {self.customer.full_name()}"