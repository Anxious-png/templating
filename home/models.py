from django.db import models
#from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MinValueValidator, RegexValidator
from django.contrib.auth.models import AbstractUser,Group, Permission
# Create your models here.

BRANCH_CHOICES = [
    ('Maganjo', 'Maganjo'),
    ('Matugga', 'Matugga'),
]

class Userprofile(AbstractUser):
    is_salesagent = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    address = models.TextField(max_length=200, blank=False)
    phonenumber = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10)
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES, null=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        related_name="userprofile_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="userprofile_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions"
    )
    def __str__(self):
       return self.username
    
# BRANCH choices model alternative

class Dealer(models.Model):
    DEALER_TYPES =[
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('own_farm', 'Own Farm'), 
    ]
    name = models.CharField(max_length=100)
    dealer_type = models.CharField(max_length=50, choices=DEALER_TYPES)
    contact = models.CharField(max_length=100,blank=True,null=True)
    location = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return self.name

class Produce(models.Model):
    name = models.CharField(max_length=100, unique=True)
    produce_type = models.CharField(max_length=50, validators=[MinLengthValidator(2)])
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
    def get_stock_for_branch(self, branch): 
        stock = self.stock.filter(branch=branch)
        return stock.quantity if stock else 0



class Procurement(models.Model):
    produce = models.ForeignKey(Produce,on_delete=models.CASCADE,blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    tonnage_kgs = models.IntegerField(
        validators=[MinValueValidator(1000)],
    
    )
    costUgx = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(10000)],
        verbose_name="Cost (UGX)"
    )
    dealername = models.ForeignKey(Dealer, on_delete=models.SET_NULL,null=True )
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES)
    contact = models.CharField(max_length=15,
        validators=[RegexValidator(regex=r'^\+?\d{9,15}$', message="Enter a valid phone number.")],
        blank=True)
    selling_price_ugx = models.FloatField(
    )
    recorded_by = models.ForeignKey(Userprofile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    def __str__(self):
           return f"Procurement of {self.produce} on {self.date}"

class Stock(models.Model):
    produce = models.ForeignKey(Produce, on_delete=models.CASCADE)
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES)
    price = models.IntegerField(default=0, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    tonnage_kgs = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
       
    
    def __str__(self):
        return f"{self.produce} - {self.branch} on {self.last_updated}"


class Sale(models.Model):
    produce = models.ForeignKey(Produce, on_delete=models.SET_NULL, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid_ugx = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(10000)],
    )
    buyer_name = models.CharField(max_length=255, validators=[MinLengthValidator(2)])
    sales_agent = models.ForeignKey(
       Userprofile,  
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def get_total(self):
        expected_sales= self.price * self.quantity
        return int(expected_sales)
    
    def get_change(self):
        change = self.get_total() - self.amount_paid_ugx
        return abs(int(change))

    def __str__(self):
        return f"{self.produce} - {self.quantity} kg sold on {self.date}"
 


class CreditSale(models.Model):
    produce = models.ForeignKey(Produce, on_delete=models.SET_NULL, verbose_name="Produce Name",null=True)
    buyer_name = models.CharField(max_length=255, verbose_name="Buyer Name", validators=[MinLengthValidator(2)])
    national_id = models.CharField(
        max_length=14,
        validators=[RegexValidator(regex=r'^[A-Z0-9]{14}$', message='Enter a valid NIN')],
    )
    location = models.CharField(max_length=255, validators=[MinLengthValidator(2)])
    contact = models.CharField(max_length=15,validators=[
        RegexValidator(regex=r'^\+?\d{9,15}$', message="Enter a valid phone number.")])
       
    amount_due_ugx = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(10000)],
       
    )
    is_paid = models.BooleanField(default=False)
    sales_agent = models.ForeignKey(
       Userprofile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    due_date = models.DateField()
    tonnage_kgs = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_dispatch = models.DateField(auto_now_add=True)
    branch = models.CharField(max_length=20, choices=BRANCH_CHOICES)

    def __str__(self):
        return f"{self.buyer_name} - {self.produce} on credit (Due: {self.due_date})"
    def total_paid(self):
        if not hasattr(self, 'payments'):
           return 0
        return sum(payment.amount_paid for payment in self.payments.all())

    def balance_due(self):
        return self.amount_due_ugx - self.total_paid()

    def is_fully_paid(self):
        return self.balance_due() <= 0
    
    def save(self, *args, **kwargs):
        if self.pk:
           self.is_paid = self.balance_due() <= 0
        super().save(*args, **kwargs)
    

class CreditPayment(models.Model):
    credit_sale = models.ForeignKey(CreditSale, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    received_by = models.ForeignKey(Userprofile, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.amount_paid} UGX on {self.payment_date} for {self.credit_sale.buyer_name}"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate payment status on the related CreditSale
        self.credit_sale.save()

    